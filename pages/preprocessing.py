"""
Preprocessing page for EDA Automation Tool
Handles file upload, data cleaning, and preprocessing operations.
"""

import streamlit as st
import pandas as pd
from core.data_processor import DataProcessor
from core.session_manager import SessionStateManager
from core.models import Dataset
from utils.missing_value_ui import show_missing_value_analysis, show_missing_value_handler
from utils.duplicate_ui import show_duplicate_analysis, show_duplicate_handler, show_advanced_duplicate_analysis
from config.settings import MAX_FILE_SIZE_MB, SUPPORTED_FILE_TYPES


def show():
    """Display the preprocessing page."""
    
    st.title("🔧 Data Preprocessing")
    st.markdown("Upload your dataset and perform data cleaning operations.")
    
    # File upload section
    show_file_upload()
    
    # Data preview section
    if SessionStateManager.is_data_loaded():
        show_data_preview()
        
        # Download section (if data has been cleaned)
        dataset = SessionStateManager.get_dataset()
        if dataset and dataset.is_cleaned():
            st.markdown("---")
            show_download_section(dataset)
        
        # Data cleaning options
        st.markdown("---")
        show_cleaning_options()
    else:
        st.info("👆 Please upload a dataset to begin preprocessing.")


def show_file_upload():
    """Display file upload interface."""
    
    st.subheader("📁 Upload Dataset")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=SUPPORTED_FILE_TYPES,
        help=f"Supported formats: {', '.join(SUPPORTED_FILE_TYPES)}. Max size: {MAX_FILE_SIZE_MB}MB"
    )
    
    if uploaded_file is not None:
        # Validate file
        is_valid, message = DataProcessor.validate_file_upload(uploaded_file)
        
        if not is_valid:
            st.error(f"❌ {message}")
            return
        
        # Load file
        try:
            with st.spinner("Loading dataset..."):
                dataset = DataProcessor.load_file(uploaded_file)
                SessionStateManager.set_dataset(dataset)
                
            st.success(f"✅ Dataset '{dataset.name}' loaded successfully!")
            
            # Show basic info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Rows", dataset.data.shape[0])
            
            with col2:
                st.metric("Columns", dataset.data.shape[1])
            
            with col3:
                st.metric("Size (MB)", f"{dataset.metadata.get('file_size_mb', 0):.2f}")
                
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")


def show_data_preview():
    """Display data preview and basic information."""
    
    dataset = SessionStateManager.get_dataset()
    if not dataset:
        return
    
    st.subheader("👀 Data Preview")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Data Sample", "Column Info", "Summary Stats"])
    
    with tab1:
        st.write("**First 10 rows:**")
        st.dataframe(dataset.data.head(10), use_container_width=True)
        
        if len(dataset.data) > 10:
            st.write("**Last 5 rows:**")
            st.dataframe(dataset.data.tail(5), use_container_width=True)
    
    with tab2:
        st.write("**Column Information:**")
        
        column_info = dataset.get_column_info()
        info_df = pd.DataFrame.from_dict(column_info, orient='index')
        
        # Format the dataframe for better display
        if not info_df.empty:
            display_df = info_df[['dtype', 'non_null_count', 'null_count', 'null_percentage', 'unique_count']]
            st.dataframe(
                display_df.style.format({
                    'null_percentage': '{:.2f}%'
                }),
                use_container_width=True
            )
    
    with tab3:
        st.write("**Summary Statistics:**")
        
        # Numeric columns summary
        numeric_cols = dataset.data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            st.write("*Numeric Columns:*")
            st.dataframe(dataset.data[numeric_cols].describe(), use_container_width=True)
        
        # Categorical columns summary
        categorical_cols = dataset.data.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            st.write("*Categorical Columns:*")
            for col in categorical_cols[:5]:  # Show first 5 categorical columns
                st.write(f"**{col}:**")
                value_counts = dataset.data[col].value_counts().head(10)
                st.write(value_counts)


def show_cleaning_options():
    """Display data cleaning options."""
    
    dataset = SessionStateManager.get_dataset()
    if not dataset:
        return
    
    st.subheader("🧹 Data Cleaning")
    
    # Show cleaning history
    if dataset.cleaning_history:
        with st.expander("📋 Cleaning History"):
            for operation in dataset.cleaning_history:
                st.text(operation)
    
    # Cleaning options tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Missing Values", "Duplicates", "Data Types", "Outliers"])
    
    with tab1:
        show_missing_values_section(dataset)
    
    with tab2:
        show_duplicates_section(dataset)
    
    with tab3:
        show_data_types_section(dataset)
    
    with tab4:
        show_outliers_section(dataset)


def show_missing_values_section(dataset: Dataset):
    """Show missing values handling section."""
    
    # Analysis
    show_missing_value_analysis(dataset.data)
    
    st.markdown("---")
    
    # Handler
    processed_df = show_missing_value_handler(dataset.data)
    
    if processed_df is not None:
        # Update dataset
        updated_dataset = Dataset(
            name=dataset.name,
            data=processed_df,
            metadata=dataset.metadata.copy(),
            cleaning_history=dataset.cleaning_history.copy(),
            quality_metrics=dataset.quality_metrics.copy()
        )
        
        SessionStateManager.update_dataset(updated_dataset, "Handled missing values")
        st.rerun()


def show_duplicates_section(dataset: Dataset):
    """Show duplicate handling section."""
    
    # Basic duplicate analysis
    show_duplicate_analysis(dataset.data)
    
    st.markdown("---")
    
    # Duplicate handler
    processed_df = show_duplicate_handler(dataset.data)
    
    if processed_df is not None:
        # Update dataset
        updated_dataset = Dataset(
            name=dataset.name,
            data=processed_df,
            metadata=dataset.metadata.copy(),
            cleaning_history=dataset.cleaning_history.copy(),
            quality_metrics=dataset.quality_metrics.copy()
        )
        
        removed_count = len(dataset.data) - len(processed_df)
        SessionStateManager.update_dataset(updated_dataset, f"Removed {removed_count} duplicate rows")
        st.rerun()
    
    # Advanced analysis (optional)
    if st.checkbox("Show Advanced Duplicate Analysis", key="advanced_duplicates"):
        st.markdown("---")
        show_advanced_duplicate_analysis(dataset.data)


def show_data_types_section(dataset: Dataset):
    """Show data type conversion section."""
    
    st.write("**Data Types:**")
    
    dtypes_df = pd.DataFrame({
        'Column': dataset.data.columns,
        'Current Type': dataset.data.dtypes.astype(str),
        'Non-null Count': dataset.data.count(),
        'Sample Values': [str(dataset.data[col].dropna().iloc[:3].tolist()) for col in dataset.data.columns]
    })
    
    st.dataframe(dtypes_df, use_container_width=True)
    
    # Auto-convert types
    if st.button("Auto-convert Data Types", type="primary"):
        try:
            converted_data = dataset.data.copy()
            conversions = []
            
            for col in converted_data.columns:
                original_dtype = converted_data[col].dtype
                
                # Try to convert to numeric
                if converted_data[col].dtype == 'object':
                    try:
                        converted_data[col] = pd.to_numeric(converted_data[col], errors='ignore')
                        if converted_data[col].dtype != original_dtype:
                            conversions.append(f"{col}: {original_dtype} → {converted_data[col].dtype}")
                    except:
                        pass
                
                # Try to convert to datetime
                if converted_data[col].dtype == 'object':
                    try:
                        converted_data[col] = pd.to_datetime(converted_data[col], errors='ignore')
                        if converted_data[col].dtype != original_dtype:
                            conversions.append(f"{col}: {original_dtype} → {converted_data[col].dtype}")
                    except:
                        pass
            
            if conversions:
                updated_dataset = Dataset(
                    name=dataset.name,
                    data=converted_data,
                    metadata=dataset.metadata.copy(),
                    cleaning_history=dataset.cleaning_history.copy(),
                    quality_metrics=dataset.quality_metrics.copy()
                )
                
                conversion_summary = "; ".join(conversions)
                SessionStateManager.update_dataset(updated_dataset, f"Auto-converted data types: {conversion_summary}")
                
                st.success(f"✅ Converted {len(conversions)} columns!")
                for conversion in conversions:
                    st.info(conversion)
                st.rerun()
            else:
                st.info("No automatic conversions were possible.")
                
        except Exception as e:
            st.error(f"Error converting data types: {str(e)}")


def show_outliers_section(dataset: Dataset):
    """Show outlier detection section."""
    
    st.write("**Outlier Detection:**")
    
    numeric_cols = dataset.data.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.info("No numeric columns found for outlier detection.")
        return
    
    # Column selection
    selected_col = st.selectbox("Select column for outlier detection:", numeric_cols)
    
    if selected_col:
        col_data = dataset.data[selected_col].dropna()
        
        # Calculate outliers using IQR method
        Q1 = col_data.quantile(0.25)
        Q3 = col_data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Values", len(col_data))
        
        with col2:
            st.metric("Outliers", len(outliers))
        
        with col3:
            outlier_percentage = (len(outliers) / len(col_data)) * 100
            st.metric("Outlier %", f"{outlier_percentage:.2f}%")
        
        if len(outliers) > 0:
            st.warning(f"Found {len(outliers)} outliers in '{selected_col}'")
            
            # Show outlier values
            if st.checkbox("Show outlier values"):
                st.write("Outlier values:")
                st.write(outliers.tolist())
            
            # Remove outliers button
            if st.button("Remove Outliers", type="primary"):
                # Remove rows with outliers in selected column
                mask = (dataset.data[selected_col] >= lower_bound) & (dataset.data[selected_col] <= upper_bound)
                cleaned_data = dataset.data[mask | dataset.data[selected_col].isna()]
                
                updated_dataset = Dataset(
                    name=dataset.name,
                    data=cleaned_data,
                    metadata=dataset.metadata.copy(),
                    cleaning_history=dataset.cleaning_history.copy(),
                    quality_metrics=dataset.quality_metrics.copy()
                )
                
                removed_count = len(dataset.data) - len(cleaned_data)
                SessionStateManager.update_dataset(updated_dataset, f"Removed {removed_count} outlier rows from '{selected_col}'")
                st.success(f"✅ Removed {removed_count} rows with outliers!")
                st.rerun()
        else:
            st.success("✅ No outliers found!")
    
    # Reset data button
    st.markdown("---")
    if st.button("🔄 Reset to Original Data", type="secondary"):
        original_dataset = SessionStateManager.get_data("original_dataset")
        if original_dataset:
            SessionStateManager.set_dataset(original_dataset)
            st.success("✅ Data reset to original!")
            st.rerun()
        else:
            st.error("Original data not found!")


def show_download_section(dataset: Dataset):
    """Display download options for cleaned dataset."""
    
    st.subheader("💾 Download Cleaned Dataset")
    
    # Show cleaning summary
    if dataset.cleaning_history:
        with st.expander("📋 View Cleaning Operations", expanded=False):
            st.write("**Operations performed:**")
            for i, operation in enumerate(dataset.cleaning_history, 1):
                st.text(f"{i}. {operation}")
    
    # Download statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Rows", dataset.data.shape[0])
    
    with col2:
        original_shape = dataset.metadata.get('original_shape', (0, 0))
        rows_removed = original_shape[0] - dataset.data.shape[0]
        st.metric("Rows Removed", rows_removed)
    
    with col3:
        if original_shape[0] > 0:
            retention_rate = (dataset.data.shape[0] / original_shape[0]) * 100
            st.metric("Data Retention", f"{retention_rate:.1f}%")
        else:
            st.metric("Data Retention", "N/A")
    
    # Download format selection
    st.write("**Select download format:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV download
        csv_data = dataset.data.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv_data,
            file_name=f"{dataset.name}_cleaned.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        # Excel download
        try:
            from io import BytesIO
            
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                dataset.data.to_excel(writer, index=False, sheet_name='Cleaned Data')
                
                # Add a summary sheet with cleaning history
                if dataset.cleaning_history:
                    summary_df = pd.DataFrame({
                        'Operation': [op.split(': ', 1)[1] if ': ' in op else op for op in dataset.cleaning_history],
                        'Timestamp': [op.split(': ', 1)[0] if ': ' in op else '' for op in dataset.cleaning_history]
                    })
                    summary_df.to_excel(writer, index=False, sheet_name='Cleaning History')
            
            excel_data = buffer.getvalue()
            
            st.download_button(
                label="📥 Download as Excel",
                data=excel_data,
                file_name=f"{dataset.name}_cleaned.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Excel export not available: {str(e)}")
    
    # Additional download options
    with st.expander("📊 Advanced Download Options"):
        st.write("**Download with metadata:**")
        
        # JSON download with metadata
        import json
        from datetime import datetime
        
        metadata_export = {
            'dataset_name': dataset.name,
            'export_timestamp': datetime.now().isoformat(),
            'original_shape': dataset.metadata.get('original_shape'),
            'current_shape': dataset.data.shape,
            'cleaning_operations': dataset.cleaning_history,
            'data_quality_metrics': {
                'completeness': ((dataset.data.shape[0] * dataset.data.shape[1] - dataset.data.isnull().sum().sum()) / 
                                (dataset.data.shape[0] * dataset.data.shape[1]) * 100) if dataset.data.shape[0] > 0 else 0,
                'missing_values': int(dataset.data.isnull().sum().sum()),
                'duplicate_rows': int(dataset.data.duplicated().sum())
            }
        }
        
        json_data = json.dumps(metadata_export, indent=2)
        
        st.download_button(
            label="📥 Download Metadata (JSON)",
            data=json_data,
            file_name=f"{dataset.name}_metadata.json",
            mime="application/json",
            use_container_width=True
        )
        
        # Download data summary report
        st.write("**Download summary report:**")
        
        summary_report = generate_summary_report(dataset)
        
        st.download_button(
            label="📥 Download Summary Report (TXT)",
            data=summary_report,
            file_name=f"{dataset.name}_summary.txt",
            mime="text/plain",
            use_container_width=True
        )


def generate_summary_report(dataset: Dataset) -> str:
    """Generate a text summary report of the dataset and cleaning operations."""
    
    from datetime import datetime
    
    report_lines = [
        "=" * 80,
        "DATA CLEANING SUMMARY REPORT",
        "=" * 80,
        "",
        f"Dataset Name: {dataset.name}",
        f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "=" * 80,
        "DATASET INFORMATION",
        "=" * 80,
        "",
        f"Original Shape: {dataset.metadata.get('original_shape', 'N/A')}",
        f"Current Shape: {dataset.data.shape}",
        f"Rows Removed: {dataset.metadata.get('original_shape', (0, 0))[0] - dataset.data.shape[0]}",
        f"Columns: {dataset.data.shape[1]}",
        "",
        "Column Names:",
        ", ".join(dataset.data.columns.tolist()),
        "",
        "=" * 80,
        "DATA QUALITY METRICS",
        "=" * 80,
        "",
        f"Total Cells: {dataset.data.shape[0] * dataset.data.shape[1]}",
        f"Missing Values: {dataset.data.isnull().sum().sum()}",
        f"Completeness: {((dataset.data.shape[0] * dataset.data.shape[1] - dataset.data.isnull().sum().sum()) / (dataset.data.shape[0] * dataset.data.shape[1]) * 100):.2f}%",
        f"Duplicate Rows: {dataset.data.duplicated().sum()}",
        "",
        "=" * 80,
        "CLEANING OPERATIONS PERFORMED",
        "=" * 80,
        ""
    ]
    
    if dataset.cleaning_history:
        for i, operation in enumerate(dataset.cleaning_history, 1):
            report_lines.append(f"{i}. {operation}")
    else:
        report_lines.append("No cleaning operations performed.")
    
    report_lines.extend([
        "",
        "=" * 80,
        "COLUMN STATISTICS",
        "=" * 80,
        ""
    ])
    
    # Add column statistics
    for col in dataset.data.columns:
        col_data = dataset.data[col]
        report_lines.append(f"\n{col}:")
        report_lines.append(f"  Data Type: {col_data.dtype}")
        report_lines.append(f"  Non-null Count: {col_data.count()}")
        report_lines.append(f"  Missing Count: {col_data.isnull().sum()}")
        report_lines.append(f"  Unique Values: {col_data.nunique()}")
        
        if pd.api.types.is_numeric_dtype(col_data):
            report_lines.append(f"  Mean: {col_data.mean():.2f}")
            report_lines.append(f"  Median: {col_data.median():.2f}")
            report_lines.append(f"  Std Dev: {col_data.std():.2f}")
            report_lines.append(f"  Min: {col_data.min():.2f}")
            report_lines.append(f"  Max: {col_data.max():.2f}")
    
    report_lines.extend([
        "",
        "=" * 80,
        "END OF REPORT",
        "=" * 80
    ])
    
    return "\n".join(report_lines)