"""
UI components for missing value handling
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional
from core.data_processor import DataProcessor


def show_missing_value_analysis(df: pd.DataFrame) -> None:
    """Display missing value analysis in Streamlit."""
    
    st.subheader("🔍 Missing Value Analysis")
    
    missing_info = DataProcessor.detect_missing_values(df)
    
    if missing_info['total_missing'] == 0:
        st.success("✅ No missing values found in the dataset!")
        return
    
    # Overall statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Missing Values", missing_info['total_missing'])
    
    with col2:
        st.metric("Missing Percentage", f"{missing_info['missing_percentage']:.2f}%")
    
    with col3:
        st.metric("Columns Affected", len(missing_info['columns_with_missing']))
    
    # Detailed breakdown by column
    if missing_info['columns_with_missing']:
        st.subheader("Missing Values by Column")
        
        missing_df = pd.DataFrame.from_dict(missing_info['columns_with_missing'], orient='index')
        missing_df = missing_df.sort_values('percentage', ascending=False)
        
        # Create a bar chart
        st.bar_chart(missing_df['percentage'])
        
        # Show detailed table
        st.dataframe(
            missing_df.style.format({'percentage': '{:.2f}%'}),
            use_container_width=True
        )
    
    # Recommendations
    if missing_info['recommendations']:
        st.subheader("💡 Recommendations")
        for rec in missing_info['recommendations']:
            st.info(rec)


def show_missing_value_handler(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Show missing value handling interface and return processed DataFrame.
    
    Args:
        df: DataFrame to process
        
    Returns:
        Processed DataFrame or None if no processing selected
    """
    
    st.subheader("🛠️ Handle Missing Values")
    
    missing_info = DataProcessor.detect_missing_values(df)
    
    if missing_info['total_missing'] == 0:
        st.info("No missing values to handle.")
        return None
    
    # Get available strategies
    strategies = DataProcessor.get_missing_value_strategies(df)
    
    # Strategy selection
    st.write("**Select handling strategy:**")
    
    strategy_options = {
        'drop': 'Drop rows with missing values',
        'drop_columns': 'Drop columns with missing values',
        'mean': 'Fill with mean (numeric only)',
        'median': 'Fill with median (numeric only)',
        'mode': 'Fill with most frequent value',
        'ffill': 'Forward fill',
        'bfill': 'Backward fill',
        'constant': 'Fill with constant value'
    }
    
    selected_strategy = st.selectbox(
        "Choose strategy:",
        options=list(strategy_options.keys()),
        format_func=lambda x: strategy_options[x],
        key="missing_strategy"
    )
    
    # Column selection for targeted handling
    columns_with_missing = list(missing_info['columns_with_missing'].keys())
    
    if len(columns_with_missing) > 1:
        st.write("**Select columns to process:**")
        
        all_columns = st.checkbox("Apply to all columns with missing values", value=True)
        
        if not all_columns:
            selected_columns = st.multiselect(
                "Choose specific columns:",
                options=columns_with_missing,
                default=columns_with_missing,
                key="missing_columns"
            )
        else:
            selected_columns = columns_with_missing
    else:
        selected_columns = columns_with_missing
    
    # Show preview of what will happen
    if selected_columns:
        st.write("**Preview of changes:**")
        
        preview_df = df[selected_columns].copy()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Before:")
            st.write(f"Missing values: {preview_df.isnull().sum().sum()}")
            st.dataframe(preview_df.head(), use_container_width=True)
        
        with col2:
            st.write("After (preview):")
            try:
                processed_preview = DataProcessor.handle_missing_values(
                    preview_df, selected_strategy, selected_columns
                )
                st.write(f"Missing values: {processed_preview.isnull().sum().sum()}")
                st.dataframe(processed_preview.head(), use_container_width=True)
            except Exception as e:
                st.error(f"Error in preview: {str(e)}")
                return None
    
    # Apply button
    if st.button("Apply Missing Value Handling", type="primary"):
        try:
            processed_df = DataProcessor.handle_missing_values(df, selected_strategy, selected_columns)
            
            # Show results
            original_missing = df.isnull().sum().sum()
            new_missing = processed_df.isnull().sum().sum()
            
            st.success(f"✅ Missing values handled successfully!")
            st.info(f"Missing values reduced from {original_missing} to {new_missing}")
            
            return processed_df
            
        except Exception as e:
            st.error(f"Error handling missing values: {str(e)}")
            return None
    
    return None


def show_column_specific_missing_handler(df: pd.DataFrame, column: str) -> Optional[pd.DataFrame]:
    """
    Show column-specific missing value handling interface.
    
    Args:
        df: DataFrame to process
        column: Specific column to handle
        
    Returns:
        Processed DataFrame or None if no processing selected
    """
    
    if column not in df.columns or not df[column].isnull().any():
        st.info(f"Column '{column}' has no missing values.")
        return None
    
    st.subheader(f"Handle Missing Values in '{column}'")
    
    # Show column statistics
    missing_count = df[column].isnull().sum()
    missing_percentage = (missing_count / len(df)) * 100
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Missing Count", missing_count)
    
    with col2:
        st.metric("Missing %", f"{missing_percentage:.2f}%")
    
    with col3:
        st.metric("Data Type", str(df[column].dtype))
    
    # Get column-specific strategies
    strategies = DataProcessor.get_missing_value_strategies(df, column)
    
    if column in strategies['column_specific']:
        col_strategies = strategies['column_specific'][column]['strategies']
        recommended = strategies['column_specific'][column]['recommended']
        
        # Strategy selection
        strategy_options = {s['name']: s['label'] for s in col_strategies if s['applicable']}
        
        selected_strategy = st.selectbox(
            "Choose strategy:",
            options=list(strategy_options.keys()),
            format_func=lambda x: strategy_options[x],
            index=list(strategy_options.keys()).index(recommended) if recommended in strategy_options else 0,
            key=f"strategy_{column}"
        )
        
        # Show preview
        st.write("**Preview:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Before:")
            st.write(df[column].describe() if pd.api.types.is_numeric_dtype(df[column]) else df[column].value_counts().head())
        
        with col2:
            st.write("After (preview):")
            try:
                processed_df = DataProcessor.handle_missing_values(df, selected_strategy, [column])
                processed_col = processed_df[column]
                st.write(processed_col.describe() if pd.api.types.is_numeric_dtype(processed_col) else processed_col.value_counts().head())
            except Exception as e:
                st.error(f"Error in preview: {str(e)}")
                return None
        
        # Apply button
        if st.button(f"Apply to '{column}'", type="primary", key=f"apply_{column}"):
            try:
                processed_df = DataProcessor.handle_missing_values(df, selected_strategy, [column])
                st.success(f"✅ Missing values in '{column}' handled successfully!")
                return processed_df
            except Exception as e:
                st.error(f"Error handling missing values: {str(e)}")
                return None
    
    return None