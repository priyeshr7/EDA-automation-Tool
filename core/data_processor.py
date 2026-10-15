"""
Data Processing Engine for EDA Automation Tool
Handles data loading, cleaning, and preprocessing operations.
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Optional, Tuple
from io import StringIO, BytesIO
import chardet
from config.settings import MAX_FILE_SIZE_MB, SUPPORTED_FILE_TYPES
from core.models import Dataset


class DataProcessor:
    """Data processing engine for loading and cleaning data."""
    
    @staticmethod
    def load_file(uploaded_file, file_type: str = None) -> Dataset:
        """
        Load file and create Dataset object.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            file_type: Optional file type override
            
        Returns:
            Dataset object with loaded data
            
        Raises:
            ValueError: If file format is not supported or file is corrupted
            MemoryError: If file is too large
        """
        try:
            # Validate file size
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            if file_size_mb > MAX_FILE_SIZE_MB:
                raise MemoryError(f"File size ({file_size_mb:.1f}MB) exceeds limit ({MAX_FILE_SIZE_MB}MB)")
            
            # Determine file type
            if file_type is None:
                file_type = uploaded_file.name.split('.')[-1].lower()
            
            if file_type not in SUPPORTED_FILE_TYPES:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Load data based on file type
            if file_type == 'csv':
                df = DataProcessor._load_csv(uploaded_file)
            elif file_type in ['xlsx', 'xls']:
                df = DataProcessor._load_excel(uploaded_file)
            elif file_type == 'json':
                df = DataProcessor._load_json(uploaded_file)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Validate loaded data
            if df.empty:
                raise ValueError("Loaded dataset is empty")
            
            # Create dataset object
            dataset = Dataset(
                name=uploaded_file.name.split('.')[0],
                data=df,
                metadata={
                    'file_type': file_type,
                    'file_size_mb': file_size_mb,
                    'upload_timestamp': pd.Timestamp.now(),
                    'original_columns': list(df.columns),
                    'original_shape': df.shape
                }
            )
            
            return dataset
            
        except Exception as e:
            raise ValueError(f"Error loading file: {str(e)}")
    
    @staticmethod
    def _load_csv(uploaded_file) -> pd.DataFrame:
        """Load CSV file with encoding detection."""
        try:
            # Try UTF-8 first
            content = uploaded_file.getvalue()
            try:
                df = pd.read_csv(StringIO(content.decode('utf-8')))
                return df
            except UnicodeDecodeError:
                # Detect encoding
                detected = chardet.detect(content)
                encoding = detected['encoding'] or 'latin-1'
                df = pd.read_csv(StringIO(content.decode(encoding)))
                return df
                
        except Exception as e:
            # Try with different parameters
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='latin-1', sep=None, engine='python')
                return df
            except Exception:
                raise ValueError(f"Could not parse CSV file: {str(e)}")
    
    @staticmethod
    def _load_excel(uploaded_file) -> pd.DataFrame:
        """Load Excel file."""
        try:
            # Try to load first sheet
            df = pd.read_excel(uploaded_file, sheet_name=0)
            return df
        except Exception as e:
            raise ValueError(f"Could not parse Excel file: {str(e)}")
    
    @staticmethod
    def _load_json(uploaded_file) -> pd.DataFrame:
        """Load JSON file."""
        try:
            content = uploaded_file.getvalue().decode('utf-8')
            data = json.loads(content)
            
            # Handle different JSON structures
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # Try to create DataFrame from dict
                try:
                    df = pd.DataFrame(data)
                except ValueError:
                    # If dict values are not lists, create single row
                    df = pd.DataFrame([data])
            else:
                raise ValueError("JSON structure not supported")
            
            return df
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Could not parse JSON file: {str(e)}")
    
    @staticmethod
    def validate_file_upload(uploaded_file) -> Tuple[bool, str]:
        """
        Validate uploaded file before processing.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if uploaded_file is None:
            return False, "No file uploaded"
        
        # Check file size
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            return False, f"File size ({file_size_mb:.1f}MB) exceeds limit ({MAX_FILE_SIZE_MB}MB)"
        
        # Check file type
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in SUPPORTED_FILE_TYPES:
            return False, f"Unsupported file type: {file_extension}. Supported types: {', '.join(SUPPORTED_FILE_TYPES)}"
        
        # Check if file is empty
        if file_size_mb == 0:
            return False, "File is empty"
        
        return True, "File validation passed"
    
    @staticmethod
    def get_data_preview(df: pd.DataFrame, max_rows: int = 100) -> Dict[str, Any]:
        """
        Generate data preview with basic information.
        
        Args:
            df: DataFrame to preview
            max_rows: Maximum number of rows to show
            
        Returns:
            Dictionary with preview information
        """
        preview = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'head': df.head(min(max_rows, len(df))).to_dict('records'),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'numeric_columns': list(df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(df.select_dtypes(include=['object', 'category']).columns),
            'datetime_columns': list(df.select_dtypes(include=['datetime64']).columns)
        }
        
        # Add basic statistics for numeric columns
        if preview['numeric_columns']:
            numeric_stats = df[preview['numeric_columns']].describe().to_dict()
            preview['numeric_summary'] = numeric_stats
        
        # Add value counts for categorical columns (top 5)
        categorical_summary = {}
        for col in preview['categorical_columns'][:5]:  # Limit to first 5 categorical columns
            value_counts = df[col].value_counts().head(5).to_dict()
            categorical_summary[col] = value_counts
        preview['categorical_summary'] = categorical_summary
        
        return preview
    
    @staticmethod
    def detect_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect and analyze missing values in dataset.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with missing value analysis
        """
        missing_info = {
            'total_missing': df.isnull().sum().sum(),
            'missing_percentage': (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100,
            'columns_with_missing': {},
            'missing_patterns': {},
            'recommendations': []
        }
        
        # Analyze missing values by column
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                missing_percentage = (missing_count / len(df)) * 100
                missing_info['columns_with_missing'][col] = {
                    'count': missing_count,
                    'percentage': missing_percentage,
                    'dtype': str(df[col].dtype)
                }
        
        # Analyze missing patterns (combinations of missing values)
        if missing_info['columns_with_missing']:
            missing_cols = list(missing_info['columns_with_missing'].keys())
            if len(missing_cols) > 1:
                # Create missing indicator matrix
                missing_matrix = df[missing_cols].isnull()
                pattern_counts = missing_matrix.value_counts().head(10)
                missing_info['missing_patterns'] = pattern_counts.to_dict()
        
        # Generate recommendations
        for col, info in missing_info['columns_with_missing'].items():
            if info['percentage'] < 5:
                missing_info['recommendations'].append(f"{col}: Low missing rate ({info['percentage']:.1f}%) - consider dropping rows")
            elif info['percentage'] < 30:
                if 'int' in info['dtype'] or 'float' in info['dtype']:
                    missing_info['recommendations'].append(f"{col}: Moderate missing rate ({info['percentage']:.1f}%) - consider mean/median imputation")
                else:
                    missing_info['recommendations'].append(f"{col}: Moderate missing rate ({info['percentage']:.1f}%) - consider mode imputation")
            else:
                missing_info['recommendations'].append(f"{col}: High missing rate ({info['percentage']:.1f}%) - consider dropping column")
        
        return missing_info
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, strategy: str, columns: List[str] = None) -> pd.DataFrame:
        """
        Handle missing values using specified strategy.
        
        Args:
            df: DataFrame to process
            strategy: Strategy to use ('drop', 'mean', 'median', 'mode', 'ffill', 'bfill', 'constant')
            columns: Specific columns to process (if None, process all columns with missing values)
            
        Returns:
            DataFrame with missing values handled
        """
        df_processed = df.copy()
        
        # Determine columns to process
        if columns is None:
            columns = df_processed.columns[df_processed.isnull().any()].tolist()
        
        if not columns:
            return df_processed  # No missing values to handle
        
        if strategy == 'drop':
            # Drop rows with any missing values in specified columns
            df_processed = df_processed.dropna(subset=columns)
            
        elif strategy == 'drop_columns':
            # Drop columns with missing values
            df_processed = df_processed.drop(columns=columns)
            
        elif strategy == 'mean':
            # Fill with mean (numeric columns only)
            for col in columns:
                if pd.api.types.is_numeric_dtype(df_processed[col]):
                    mean_value = df_processed[col].mean()
                    df_processed[col].fillna(mean_value, inplace=True)
                    
        elif strategy == 'median':
            # Fill with median (numeric columns only)
            for col in columns:
                if pd.api.types.is_numeric_dtype(df_processed[col]):
                    median_value = df_processed[col].median()
                    df_processed[col].fillna(median_value, inplace=True)
                    
        elif strategy == 'mode':
            # Fill with mode (most frequent value)
            for col in columns:
                mode_value = df_processed[col].mode()
                if not mode_value.empty:
                    df_processed[col].fillna(mode_value.iloc[0], inplace=True)
                    
        elif strategy == 'ffill':
            # Forward fill
            df_processed[columns] = df_processed[columns].ffill()
            
        elif strategy == 'bfill':
            # Backward fill
            df_processed[columns] = df_processed[columns].bfill()
            
        elif strategy == 'constant':
            # Fill with constant value (0 for numeric, 'Unknown' for categorical)
            for col in columns:
                if pd.api.types.is_numeric_dtype(df_processed[col]):
                    df_processed[col].fillna(0, inplace=True)
                else:
                    df_processed[col].fillna('Unknown', inplace=True)
                    
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        return df_processed
    
    @staticmethod
    def get_missing_value_strategies(df: pd.DataFrame, column: str = None) -> Dict[str, Any]:
        """
        Get appropriate missing value strategies for dataset or specific column.
        
        Args:
            df: DataFrame to analyze
            column: Specific column to analyze (if None, analyze all columns)
            
        Returns:
            Dictionary with strategy recommendations
        """
        strategies = {
            'general_strategies': [
                {'name': 'drop', 'label': 'Drop rows with missing values', 'applicable': True},
                {'name': 'drop_columns', 'label': 'Drop columns with missing values', 'applicable': True}
            ],
            'column_specific': {}
        }
        
        columns_to_analyze = [column] if column else df.columns[df.isnull().any()].tolist()
        
        for col in columns_to_analyze:
            if col not in df.columns or not df[col].isnull().any():
                continue
                
            col_strategies = []
            missing_percentage = (df[col].isnull().sum() / len(df)) * 100
            
            if pd.api.types.is_numeric_dtype(df[col]):
                col_strategies.extend([
                    {'name': 'mean', 'label': f'Fill with mean ({df[col].mean():.2f})', 'applicable': True},
                    {'name': 'median', 'label': f'Fill with median ({df[col].median():.2f})', 'applicable': True},
                    {'name': 'constant', 'label': 'Fill with 0', 'applicable': True}
                ])
            else:
                mode_val = df[col].mode()
                mode_label = mode_val.iloc[0] if not mode_val.empty else 'N/A'
                col_strategies.extend([
                    {'name': 'mode', 'label': f'Fill with mode ({mode_label})', 'applicable': not mode_val.empty},
                    {'name': 'constant', 'label': 'Fill with "Unknown"', 'applicable': True}
                ])
            
            # Add forward/backward fill if data has some order
            col_strategies.extend([
                {'name': 'ffill', 'label': 'Forward fill', 'applicable': True},
                {'name': 'bfill', 'label': 'Backward fill', 'applicable': True}
            ])
            
            # Add recommendations based on missing percentage
            if missing_percentage < 5:
                recommendation = 'drop'
            elif missing_percentage > 50:
                recommendation = 'drop_columns'
            elif pd.api.types.is_numeric_dtype(df[col]):
                recommendation = 'median'
            else:
                recommendation = 'mode'
            
            strategies['column_specific'][col] = {
                'strategies': col_strategies,
                'missing_count': df[col].isnull().sum(),
                'missing_percentage': missing_percentage,
                'dtype': str(df[col].dtype),
                'recommended': recommendation
            }
        
        return strategies
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: List[str] = None, keep: str = 'first') -> pd.DataFrame:
        """
        Remove duplicate rows from DataFrame.
        
        Args:
            df: DataFrame to process
            subset: Columns to consider for identifying duplicates (if None, use all columns)
            keep: Which duplicates to keep ('first', 'last', False for remove all)
            
        Returns:
            DataFrame with duplicates removed
        """
        try:
            if subset is not None:
                # Validate that subset columns exist
                missing_cols = [col for col in subset if col not in df.columns]
                if missing_cols:
                    raise ValueError(f"Columns not found in DataFrame: {missing_cols}")
            
            # Remove duplicates
            df_cleaned = df.drop_duplicates(subset=subset, keep=keep)
            
            return df_cleaned
            
        except Exception as e:
            raise ValueError(f"Error removing duplicates: {str(e)}")
    
    @staticmethod
    def detect_duplicates(df: pd.DataFrame, subset: List[str] = None) -> Dict[str, Any]:
        """
        Detect and analyze duplicate rows in dataset.
        
        Args:
            df: DataFrame to analyze
            subset: Columns to consider for identifying duplicates (if None, use all columns)
            
        Returns:
            Dictionary with duplicate analysis
        """
        duplicate_info = {
            'total_duplicates': 0,
            'duplicate_percentage': 0.0,
            'duplicate_rows': pd.DataFrame(),
            'duplicate_groups': {},
            'column_analysis': {},
            'recommendations': []
        }
        
        try:
            # Detect duplicates
            if subset is not None:
                # Validate subset columns
                missing_cols = [col for col in subset if col not in df.columns]
                if missing_cols:
                    raise ValueError(f"Columns not found in DataFrame: {missing_cols}")
                
                duplicate_mask = df.duplicated(subset=subset, keep=False)
                duplicate_count = df.duplicated(subset=subset).sum()
            else:
                duplicate_mask = df.duplicated(keep=False)
                duplicate_count = df.duplicated().sum()
            
            duplicate_info['total_duplicates'] = duplicate_count
            duplicate_info['duplicate_percentage'] = (duplicate_count / len(df)) * 100 if len(df) > 0 else 0
            
            # Get duplicate rows
            if duplicate_count > 0:
                duplicate_rows = df[duplicate_mask].copy()
                duplicate_info['duplicate_rows'] = duplicate_rows
                
                # Analyze duplicate groups
                if subset is not None:
                    grouped = duplicate_rows.groupby(subset)
                else:
                    # For full row duplicates, group by all columns
                    grouped = duplicate_rows.groupby(list(df.columns))
                
                duplicate_groups = {}
                for name, group in grouped:
                    if len(group) > 1:  # Only include actual duplicate groups
                        group_key = str(name) if isinstance(name, tuple) else str(name)
                        duplicate_groups[group_key] = {
                            'count': len(group),
                            'indices': group.index.tolist(),
                            'first_occurrence': group.index[0]
                        }
                
                duplicate_info['duplicate_groups'] = duplicate_groups
            
            # Column-wise duplicate analysis (analyze all columns)
            column_analysis = {}
            for col in df.columns:
                col_duplicates = df[col].duplicated().sum()
                col_unique = df[col].nunique()
                col_analysis[col] = {
                    'duplicate_values': col_duplicates,
                    'unique_values': col_unique,
                    'duplicate_percentage': (col_duplicates / len(df)) * 100 if len(df) > 0 else 0,
                    'uniqueness_ratio': (col_unique / len(df)) * 100 if len(df) > 0 else 0
                }
            
            duplicate_info['column_analysis'] = column_analysis
            
            # Generate recommendations
            if duplicate_count == 0:
                duplicate_info['recommendations'].append("No duplicate rows found. Data appears to be clean.")
            elif duplicate_info['duplicate_percentage'] < 1:
                duplicate_info['recommendations'].append(f"Low duplicate rate ({duplicate_info['duplicate_percentage']:.2f}%) - safe to remove duplicates")
            elif duplicate_info['duplicate_percentage'] < 10:
                duplicate_info['recommendations'].append(f"Moderate duplicate rate ({duplicate_info['duplicate_percentage']:.2f}%) - review duplicates before removal")
            else:
                duplicate_info['recommendations'].append(f"High duplicate rate ({duplicate_info['duplicate_percentage']:.2f}%) - investigate data source quality")
            
            # Column-specific recommendations
            high_duplicate_cols = [col for col, info in column_analysis.items() 
                                 if info['duplicate_percentage'] > 50]
            if high_duplicate_cols:
                duplicate_info['recommendations'].append(f"Columns with high duplicate values: {', '.join(high_duplicate_cols)} - consider if these are categorical variables")
            
            low_uniqueness_cols = [col for col, info in column_analysis.items() 
                                 if info['uniqueness_ratio'] < 10 and col not in high_duplicate_cols]
            if low_uniqueness_cols:
                duplicate_info['recommendations'].append(f"Columns with low uniqueness: {', '.join(low_uniqueness_cols)} - may be good candidates for grouping")
            
        except Exception as e:
            duplicate_info['error'] = str(e)
            duplicate_info['recommendations'].append(f"Error in duplicate analysis: {str(e)}")
        
        # Always perform column analysis, even if there was an error above
        if not duplicate_info['column_analysis']:  # Only if not already populated
            try:
                column_analysis = {}
                for col in df.columns:
                    col_duplicates = df[col].duplicated().sum()
                    col_unique = df[col].nunique()
                    column_analysis[col] = {
                        'duplicate_values': col_duplicates,
                        'unique_values': col_unique,
                        'duplicate_percentage': (col_duplicates / len(df)) * 100 if len(df) > 0 else 0,
                        'uniqueness_ratio': (col_unique / len(df)) * 100 if len(df) > 0 else 0
                    }
                duplicate_info['column_analysis'] = column_analysis
            except Exception:
                pass  # If column analysis fails, just leave it empty
        
        return duplicate_info
    
    @staticmethod
    def get_duplicate_removal_strategies(df: pd.DataFrame, subset: List[str] = None) -> Dict[str, Any]:
        """
        Get duplicate removal strategies and options.
        
        Args:
            df: DataFrame to analyze
            subset: Columns to consider for duplicates
            
        Returns:
            Dictionary with removal strategies and recommendations
        """
        strategies = {
            'keep_options': [
                {'value': 'first', 'label': 'Keep first occurrence', 'description': 'Keep the first duplicate row, remove subsequent ones'},
                {'value': 'last', 'label': 'Keep last occurrence', 'description': 'Keep the last duplicate row, remove previous ones'},
                {'value': False, 'label': 'Remove all duplicates', 'description': 'Remove all duplicate rows (keep none)'}
            ],
            'subset_options': {
                'all_columns': 'Consider all columns for duplicate detection',
                'custom_subset': 'Select specific columns for duplicate detection'
            },
            'column_suggestions': [],
            'recommended_strategy': 'first'
        }
        
        # Analyze columns to suggest good candidates for subset
        if len(df.columns) > 1:
            column_suggestions = []
            
            # Suggest columns with high uniqueness as good candidates
            for col in df.columns:
                uniqueness = df[col].nunique() / len(df) if len(df) > 0 else 0
                if uniqueness > 0.8:  # High uniqueness
                    column_suggestions.append({
                        'column': col,
                        'reason': f'High uniqueness ({uniqueness:.2%}) - likely identifier',
                        'priority': 'high'
                    })
                elif uniqueness > 0.5:  # Moderate uniqueness
                    column_suggestions.append({
                        'column': col,
                        'reason': f'Moderate uniqueness ({uniqueness:.2%}) - potential key column',
                        'priority': 'medium'
                    })
            
            strategies['column_suggestions'] = column_suggestions
        
        # Determine recommended strategy based on data characteristics
        duplicate_info = DataProcessor.detect_duplicates(df, subset)
        
        if duplicate_info['duplicate_percentage'] < 1:
            strategies['recommended_strategy'] = 'first'
            strategies['recommendation_reason'] = 'Low duplicate rate - keeping first occurrence is typically safe'
        elif duplicate_info['duplicate_percentage'] > 20:
            strategies['recommended_strategy'] = 'first'
            strategies['recommendation_reason'] = 'High duplicate rate - review data quality and keep first occurrence'
        else:
            strategies['recommended_strategy'] = 'first'
            strategies['recommendation_reason'] = 'Standard approach - keep first occurrence of duplicates'
        
        return strategies