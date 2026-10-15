"""
Unit tests for DataProcessor
"""

import pytest
import pandas as pd
import numpy as np
from io import StringIO, BytesIO
import json
from unittest.mock import Mock, patch
from core.data_processor import DataProcessor
from core.models import Dataset


class TestDataProcessor:
    """Test cases for DataProcessor class."""
    
    def setup_method(self):
        """Set up test data."""
        self.test_csv_content = """name,age,city,salary
John,25,New York,50000
Jane,30,Boston,60000
Bob,35,Chicago,55000
Alice,,Seattle,65000
Charlie,40,,70000"""
        
        self.test_json_content = [
            {"name": "John", "age": 25, "city": "New York"},
            {"name": "Jane", "age": 30, "city": "Boston"},
            {"name": "Bob", "age": 35, "city": "Chicago"}
        ]
        
        self.test_df = pd.DataFrame({
            'numeric_col': [1, 2, 3, None, 5],
            'categorical_col': ['A', 'B', 'A', 'C', None],
            'mixed_col': [1, 'text', 3, None, 5]
        })
    
    def create_mock_file(self, content: str, filename: str = "test.csv") -> Mock:
        """Create mock uploaded file."""
        mock_file = Mock()
        mock_file.name = filename
        mock_file.getvalue.return_value = content.encode('utf-8')
        mock_file.read.return_value = content.encode('utf-8')
        return mock_file
    
    def test_validate_file_upload_valid(self):
        """Test file upload validation with valid file."""
        mock_file = self.create_mock_file(self.test_csv_content, "test.csv")
        
        is_valid, message = DataProcessor.validate_file_upload(mock_file)
        
        assert is_valid == True
        assert "validation passed" in message.lower()
    
    def test_validate_file_upload_no_file(self):
        """Test file upload validation with no file."""
        is_valid, message = DataProcessor.validate_file_upload(None)
        
        assert is_valid == False
        assert "no file uploaded" in message.lower()
    
    def test_validate_file_upload_unsupported_type(self):
        """Test file upload validation with unsupported file type."""
        mock_file = self.create_mock_file(self.test_csv_content, "test.txt")
        
        is_valid, message = DataProcessor.validate_file_upload(mock_file)
        
        assert is_valid == False
        assert "unsupported file type" in message.lower()
    
    def test_validate_file_upload_empty_file(self):
        """Test file upload validation with empty file."""
        mock_file = Mock()
        mock_file.name = "test.csv"
        mock_file.getvalue.return_value = b""
        
        is_valid, message = DataProcessor.validate_file_upload(mock_file)
        
        assert is_valid == False
        assert "empty" in message.lower()
    
    @patch('core.data_processor.pd.read_csv')
    def test_load_csv_file(self, mock_read_csv):
        """Test CSV file loading."""
        # Setup mock
        expected_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['A', 'B', 'C']})
        mock_read_csv.return_value = expected_df
        
        mock_file = self.create_mock_file(self.test_csv_content, "test.csv")
        
        dataset = DataProcessor.load_file(mock_file, 'csv')
        
        assert isinstance(dataset, Dataset)
        assert dataset.name == "test"
        assert dataset.metadata['file_type'] == 'csv'
        assert 'upload_timestamp' in dataset.metadata
    
    def test_load_json_file_list(self):
        """Test JSON file loading with list structure."""
        json_content = json.dumps(self.test_json_content)
        mock_file = self.create_mock_file(json_content, "test.json")
        
        dataset = DataProcessor.load_file(mock_file, 'json')
        
        assert isinstance(dataset, Dataset)
        assert dataset.name == "test"
        assert dataset.data.shape[0] == 3
        assert 'name' in dataset.data.columns
    
    def test_load_json_file_dict(self):
        """Test JSON file loading with dict structure."""
        json_dict = {"col1": [1, 2, 3], "col2": ["A", "B", "C"]}
        json_content = json.dumps(json_dict)
        mock_file = self.create_mock_file(json_content, "test.json")
        
        dataset = DataProcessor.load_file(mock_file, 'json')
        
        assert isinstance(dataset, Dataset)
        assert dataset.data.shape == (3, 2)
    
    def test_get_data_preview(self):
        """Test data preview generation."""
        preview = DataProcessor.get_data_preview(self.test_df)
        
        assert preview['shape'] == (5, 3)
        assert len(preview['columns']) == 3
        assert 'numeric_col' in preview['numeric_columns']
        assert 'categorical_col' in preview['categorical_columns']
        assert preview['missing_values']['numeric_col'] == 1
        assert preview['duplicate_rows'] == 0
        assert 'head' in preview
        assert len(preview['head']) <= 5
    
    def test_get_data_preview_with_numeric_summary(self):
        """Test data preview with numeric summary."""
        df_numeric = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': [10, 20, 30, 40, 50]
        })
        
        preview = DataProcessor.get_data_preview(df_numeric)
        
        assert 'numeric_summary' in preview
        assert 'col1' in preview['numeric_summary']
        assert 'mean' in preview['numeric_summary']['col1']
    
    def test_detect_missing_values(self):
        """Test missing value detection."""
        missing_info = DataProcessor.detect_missing_values(self.test_df)
        
        assert missing_info['total_missing'] == 3
        assert missing_info['missing_percentage'] > 0
        assert 'numeric_col' in missing_info['columns_with_missing']
        assert 'categorical_col' in missing_info['columns_with_missing']
        assert len(missing_info['recommendations']) > 0
    
    def test_detect_missing_values_no_missing(self):
        """Test missing value detection with no missing values."""
        df_complete = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['A', 'B', 'C', 'D', 'E']
        })
        
        missing_info = DataProcessor.detect_missing_values(df_complete)
        
        assert missing_info['total_missing'] == 0
        assert missing_info['missing_percentage'] == 0
        assert len(missing_info['columns_with_missing']) == 0
        assert len(missing_info['recommendations']) == 0
    
    def test_detect_missing_values_recommendations(self):
        """Test missing value recommendations."""
        # Create DataFrame with different missing percentages
        df_missing = pd.DataFrame({
            'low_missing': [1, 2, 3, 4, None],  # 20% missing
            'high_missing': [1, None, None, None, None],  # 80% missing
            'no_missing': [1, 2, 3, 4, 5]  # 0% missing
        })
        
        missing_info = DataProcessor.detect_missing_values(df_missing)
        
        recommendations = missing_info['recommendations']
        assert len(recommendations) == 2  # Only columns with missing values
        
        # Check that recommendations mention appropriate strategies
        rec_text = ' '.join(recommendations).lower()
        assert 'imputation' in rec_text or 'dropping' in rec_text
    
    def test_handle_missing_values_drop(self):
        """Test missing value handling with drop strategy."""
        df_with_missing = pd.DataFrame({
            'col1': [1, 2, None, 4, 5],
            'col2': ['A', 'B', 'C', None, 'E']
        })
        
        result = DataProcessor.handle_missing_values(df_with_missing, 'drop')
        
        # Should have 3 rows (dropped 2 rows with missing values)
        assert result.shape[0] == 3
        assert result.isnull().sum().sum() == 0
    
    def test_handle_missing_values_mean(self):
        """Test missing value handling with mean strategy."""
        df_with_missing = pd.DataFrame({
            'numeric_col': [1, 2, None, 4, 5],
            'text_col': ['A', 'B', 'C', 'D', 'E']
        })
        
        result = DataProcessor.handle_missing_values(df_with_missing, 'mean', ['numeric_col'])
        
        # Missing value should be filled with mean (3.0)
        assert result['numeric_col'].isnull().sum() == 0
        assert result['numeric_col'].iloc[2] == 3.0
        # Text column should be unchanged
        assert result['text_col'].equals(df_with_missing['text_col'])
    
    def test_handle_missing_values_median(self):
        """Test missing value handling with median strategy."""
        df_with_missing = pd.DataFrame({
            'numeric_col': [1, 2, None, 4, 5]
        })
        
        result = DataProcessor.handle_missing_values(df_with_missing, 'median', ['numeric_col'])
        
        # Missing value should be filled with median (3.0)
        assert result['numeric_col'].isnull().sum() == 0
        assert result['numeric_col'].iloc[2] == 3.0
    
    def test_handle_missing_values_mode(self):
        """Test missing value handling with mode strategy."""
        df_with_missing = pd.DataFrame({
            'categorical_col': ['A', 'B', 'A', None, 'A']
        })
        
        result = DataProcessor.handle_missing_values(df_with_missing, 'mode', ['categorical_col'])
        
        # Missing value should be filled with mode ('A')
        assert result['categorical_col'].isnull().sum() == 0
        assert result['categorical_col'].iloc[3] == 'A'
    
    def test_handle_missing_values_constant(self):
        """Test missing value handling with constant strategy."""
        df_with_missing = pd.DataFrame({
            'numeric_col': [1, 2, None, 4, 5],
            'text_col': ['A', 'B', None, 'D', 'E']
        })
        
        result = DataProcessor.handle_missing_values(df_with_missing, 'constant')
        
        # Numeric missing should be filled with 0
        assert result['numeric_col'].iloc[2] == 0
        # Text missing should be filled with 'Unknown'
        assert result['text_col'].iloc[2] == 'Unknown'
        assert result.isnull().sum().sum() == 0
    
    def test_handle_missing_values_no_missing(self):
        """Test missing value handling with no missing values."""
        df_complete = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['A', 'B', 'C', 'D', 'E']
        })
        
        result = DataProcessor.handle_missing_values(df_complete, 'drop')
        
        # Should return identical DataFrame
        assert result.equals(df_complete)
    
    def test_get_missing_value_strategies(self):
        """Test missing value strategy recommendations."""
        df_with_missing = pd.DataFrame({
            'numeric_col': [1, 2, None, 4, 5],
            'categorical_col': ['A', 'B', None, 'C', 'A'],
            'complete_col': [1, 2, 3, 4, 5]
        })
        
        strategies = DataProcessor.get_missing_value_strategies(df_with_missing)
        
        assert 'general_strategies' in strategies
        assert 'column_specific' in strategies
        
        # Should have strategies for columns with missing values
        assert 'numeric_col' in strategies['column_specific']
        assert 'categorical_col' in strategies['column_specific']
        assert 'complete_col' not in strategies['column_specific']
        
        # Check numeric column strategies
        numeric_strategies = strategies['column_specific']['numeric_col']['strategies']
        strategy_names = [s['name'] for s in numeric_strategies]
        assert 'mean' in strategy_names
        assert 'median' in strategy_names
        
        # Check categorical column strategies
        cat_strategies = strategies['column_specific']['categorical_col']['strategies']
        cat_strategy_names = [s['name'] for s in cat_strategies]
        assert 'mode' in cat_strategy_names
    
    def test_get_missing_value_strategies_single_column(self):
        """Test missing value strategies for single column."""
        df_with_missing = pd.DataFrame({
            'numeric_col': [1, 2, None, 4, 5],
            'complete_col': [1, 2, 3, 4, 5]
        })
        
        strategies = DataProcessor.get_missing_value_strategies(df_with_missing, 'numeric_col')
        
        assert 'numeric_col' in strategies['column_specific']
        assert 'complete_col' not in strategies['column_specific']
        
        # Should have recommended strategy
        assert 'recommended' in strategies['column_specific']['numeric_col']
    
    def test_detect_duplicates_no_duplicates(self):
        """Test duplicate detection with no duplicates."""
        df_unique = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['A', 'B', 'C', 'D', 'E']
        })
        
        duplicate_info = DataProcessor.detect_duplicates(df_unique)
        
        assert duplicate_info['total_duplicates'] == 0
        assert duplicate_info['duplicate_percentage'] == 0
        assert len(duplicate_info['duplicate_rows']) == 0
        assert len(duplicate_info['duplicate_groups']) == 0
    
    def test_detect_duplicates_with_duplicates(self):
        """Test duplicate detection with duplicates."""
        df_with_dups = pd.DataFrame({
            'col1': [1, 2, 1, 3, 2],
            'col2': ['A', 'B', 'A', 'C', 'B']
        })
        
        duplicate_info = DataProcessor.detect_duplicates(df_with_dups)
        
        assert duplicate_info['total_duplicates'] == 2  # Two duplicate rows
        assert duplicate_info['duplicate_percentage'] == 40.0  # 2 out of 5 rows
        assert len(duplicate_info['duplicate_rows']) == 4  # All rows involved in duplicates
        assert len(duplicate_info['duplicate_groups']) == 2  # Two duplicate groups
    
    def test_detect_duplicates_subset_columns(self):
        """Test duplicate detection with subset of columns."""
        df_subset_dups = pd.DataFrame({
            'id': [1, 2, 1, 3],
            'name': ['A', 'B', 'A', 'C'],
            'value': [10, 20, 30, 40]  # Different values for same id/name
        })
        
        # Detect duplicates based on id and name only
        duplicate_info = DataProcessor.detect_duplicates(df_subset_dups, subset=['id', 'name'])
        
        assert duplicate_info['total_duplicates'] == 1  # One duplicate based on id/name
        assert len(duplicate_info['duplicate_groups']) == 1
    
    def test_remove_duplicates_keep_first(self):
        """Test duplicate removal keeping first occurrence."""
        df_with_dups = pd.DataFrame({
            'col1': [1, 2, 1, 3, 2],
            'col2': ['A', 'B', 'A', 'C', 'B']
        })
        
        result = DataProcessor.remove_duplicates(df_with_dups, keep='first')
        
        assert len(result) == 3  # Should have 3 unique rows
        assert result.iloc[0]['col1'] == 1  # First occurrence of (1, 'A')
        assert result.iloc[1]['col1'] == 2  # First occurrence of (2, 'B')
        assert result.iloc[2]['col1'] == 3  # Unique row
    
    def test_remove_duplicates_keep_last(self):
        """Test duplicate removal keeping last occurrence."""
        df_with_dups = pd.DataFrame({
            'col1': [1, 2, 1, 3, 2],
            'col2': ['A', 'B', 'A', 'C', 'B']
        })
        
        result = DataProcessor.remove_duplicates(df_with_dups, keep='last')
        
        assert len(result) == 3  # Should have 3 unique rows
        # Should keep last occurrences (indices 2, 4, 3)
        expected_indices = [2, 3, 4]
        assert list(result.index) == expected_indices
    
    def test_remove_duplicates_keep_none(self):
        """Test duplicate removal keeping no duplicates."""
        df_with_dups = pd.DataFrame({
            'col1': [1, 2, 1, 3, 2],
            'col2': ['A', 'B', 'A', 'C', 'B']
        })
        
        result = DataProcessor.remove_duplicates(df_with_dups, keep=False)
        
        assert len(result) == 1  # Should only keep the unique row
        assert result.iloc[0]['col1'] == 3  # Only the unique row
    
    def test_remove_duplicates_subset_columns(self):
        """Test duplicate removal with subset of columns."""
        df_subset_dups = pd.DataFrame({
            'id': [1, 2, 1, 3],
            'name': ['A', 'B', 'A', 'C'],
            'value': [10, 20, 30, 40]
        })
        
        result = DataProcessor.remove_duplicates(df_subset_dups, subset=['id', 'name'], keep='first')
        
        assert len(result) == 3  # Should remove one duplicate based on id/name
        # Should keep first occurrence of id=1, name='A' (with value=10)
        first_row = result[result['id'] == 1]
        assert len(first_row) == 1
        assert first_row.iloc[0]['value'] == 10
    
    def test_remove_duplicates_invalid_subset(self):
        """Test duplicate removal with invalid subset columns."""
        df_test = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['A', 'B', 'C']
        })
        
        with pytest.raises(ValueError, match="Columns not found"):
            DataProcessor.remove_duplicates(df_test, subset=['nonexistent_col'])
    
    def test_get_duplicate_removal_strategies(self):
        """Test duplicate removal strategy recommendations."""
        df_with_dups = pd.DataFrame({
            'id': [1, 2, 1, 3, 2],  # High uniqueness column
            'category': ['A', 'A', 'A', 'B', 'B'],  # Low uniqueness column
            'value': [10, 20, 30, 40, 50]
        })
        
        strategies = DataProcessor.get_duplicate_removal_strategies(df_with_dups)
        
        assert 'keep_options' in strategies
        assert 'subset_options' in strategies
        assert 'column_suggestions' in strategies
        assert 'recommended_strategy' in strategies
        
        # Should have 3 keep options
        assert len(strategies['keep_options']) == 3
        
        # Should suggest high uniqueness columns
        suggestions = strategies['column_suggestions']
        high_priority_cols = [s['column'] for s in suggestions if s['priority'] == 'high']
        assert 'id' in high_priority_cols or 'value' in high_priority_cols
    
    def test_detect_duplicates_column_analysis(self):
        """Test column-wise duplicate analysis."""
        df_mixed = pd.DataFrame({
            'unique_col': [1, 2, 3, 4, 5],  # No duplicates
            'some_dups': [1, 1, 2, 3, 3],   # Some duplicates
            'many_dups': ['A', 'A', 'A', 'B', 'B']  # Many duplicates
        })
        
        duplicate_info = DataProcessor.detect_duplicates(df_mixed)
        
        col_analysis = duplicate_info['column_analysis']
        
        # All columns should be analyzed
        assert 'unique_col' in col_analysis
        assert 'some_dups' in col_analysis
        assert 'many_dups' in col_analysis
        
        # Check unique column
        assert col_analysis['unique_col']['duplicate_values'] == 0
        assert col_analysis['unique_col']['uniqueness_ratio'] == 100.0
        
        # Check column with some duplicates
        assert col_analysis['some_dups']['duplicate_values'] == 2
        assert col_analysis['some_dups']['uniqueness_ratio'] == 60.0  # 3 unique out of 5
        
        # Check column with many duplicates
        assert col_analysis['many_dups']['duplicate_values'] == 3
        assert col_analysis['many_dups']['uniqueness_ratio'] == 40.0  # 2 unique out of 5


if __name__ == "__main__":
    pytest.main([__file__])