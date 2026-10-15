"""
UI components for duplicate detection and removal
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional
from core.data_processor import DataProcessor


def show_duplicate_analysis(df: pd.DataFrame, subset: List[str] = None) -> None:
    """Display duplicate analysis in Streamlit."""
    
    st.subheader("🔍 Duplicate Analysis")
    
    duplicate_info = DataProcessor.detect_duplicates(df, subset)
    
    if 'error' in duplicate_info:
        st.error(f"Error in duplicate analysis: {duplicate_info['error']}")
        return
    
    if duplicate_info['total_duplicates'] == 0:
        st.success("✅ No duplicate rows found in the dataset!")
        return
    
    # Overall statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Duplicates", duplicate_info['total_duplicates'])
    
    with col2:
        st.metric("Duplicate Percentage", f"{duplicate_info['duplicate_percentage']:.2f}%")
    
    with col3:
        st.metric("Unique Groups", len(duplicate_info['duplicate_groups']))
    
    # Show duplicate groups
    if duplicate_info['duplicate_groups']:
        st.subheader("Duplicate Groups")
        
        # Show summary of duplicate groups
        group_summary = []
        for group_key, group_info in duplicate_info['duplicate_groups'].items():
            group_summary.append({
                'Group': group_key[:50] + "..." if len(group_key) > 50 else group_key,
                'Count': group_info['count'],
                'First Index': group_info['first_occurrence']
            })
        
        if group_summary:
            summary_df = pd.DataFrame(group_summary)
            st.dataframe(summary_df, use_container_width=True)
        
        # Show actual duplicate rows (limited)
        if len(duplicate_info['duplicate_rows']) > 0:
            st.write("**Sample Duplicate Rows:**")
            sample_size = min(20, len(duplicate_info['duplicate_rows']))
            st.dataframe(
                duplicate_info['duplicate_rows'].head(sample_size),
                use_container_width=True
            )
            
            if len(duplicate_info['duplicate_rows']) > sample_size:
                st.info(f"Showing {sample_size} of {len(duplicate_info['duplicate_rows'])} duplicate rows")
    
    # Column-wise analysis
    if duplicate_info['column_analysis']:
        st.subheader("Column-wise Duplicate Analysis")
        
        col_analysis_df = pd.DataFrame.from_dict(
            duplicate_info['column_analysis'], 
            orient='index'
        )
        
        # Format the dataframe for better display
        col_analysis_df = col_analysis_df.round(2)
        st.dataframe(
            col_analysis_df.style.format({
                'duplicate_percentage': '{:.2f}%',
                'uniqueness_ratio': '{:.2f}%'
            }),
            use_container_width=True
        )
    
    # Recommendations
    if duplicate_info['recommendations']:
        st.subheader("💡 Recommendations")
        for rec in duplicate_info['recommendations']:
            st.info(rec)


def show_duplicate_handler(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Show duplicate handling interface and return processed DataFrame.
    
    Args:
        df: DataFrame to process
        
    Returns:
        Processed DataFrame or None if no processing selected
    """
    
    st.subheader("🛠️ Remove Duplicates")
    
    # Get duplicate removal strategies
    strategies = DataProcessor.get_duplicate_removal_strategies(df)
    
    # Column subset selection
    st.write("**Select columns for duplicate detection:**")
    
    use_all_columns = st.radio(
        "Detection method:",
        options=[True, False],
        format_func=lambda x: "All columns" if x else "Specific columns",
        key="duplicate_detection_method"
    )
    
    selected_columns = None
    if not use_all_columns:
        selected_columns = st.multiselect(
            "Choose columns:",
            options=list(df.columns),
            default=list(df.columns),
            help="Select columns to consider when identifying duplicates",
            key="duplicate_columns"
        )
        
        if not selected_columns:
            st.warning("Please select at least one column for duplicate detection.")
            return None
    
    # Show column suggestions if available
    if not use_all_columns and strategies.get('column_suggestions'):
        with st.expander("💡 Column Selection Suggestions"):
            for suggestion in strategies['column_suggestions']:
                priority_color = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(suggestion['priority'], '⚪')
                
                st.write(f"{priority_color} **{suggestion['column']}**: {suggestion['reason']}")
    
    # Keep strategy selection
    st.write("**Select duplicate handling strategy:**")
    
    keep_options = {opt['value']: opt['label'] for opt in strategies['keep_options']}
    selected_keep = st.selectbox(
        "Which duplicates to keep:",
        options=list(keep_options.keys()),
        format_func=lambda x: keep_options[x],
        index=0,  # Default to 'first'
        key="duplicate_keep_strategy"
    )
    
    # Show strategy descriptions
    for opt in strategies['keep_options']:
        if opt['value'] == selected_keep:
            st.info(f"**Strategy:** {opt['description']}")
            break
    
    # Preview changes
    st.write("**Preview of changes:**")
    
    try:
        # Analyze current duplicates
        current_duplicates = DataProcessor.detect_duplicates(df, selected_columns)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Before:**")
            st.metric("Total Rows", len(df))
            st.metric("Duplicate Rows", current_duplicates['total_duplicates'])
            st.metric("Duplicate %", f"{current_duplicates['duplicate_percentage']:.2f}%")
        
        with col2:
            st.write("**After (preview):**")
            
            # Calculate what would happen
            if selected_keep == False:
                # Remove all duplicates
                if selected_columns:
                    remaining_rows = len(df) - len(df[df.duplicated(subset=selected_columns, keep=False)])
                else:
                    remaining_rows = len(df) - len(df[df.duplicated(keep=False)])
            else:
                # Keep first or last
                if selected_columns:
                    remaining_rows = len(df) - df.duplicated(subset=selected_columns, keep=selected_keep).sum()
                else:
                    remaining_rows = len(df) - df.duplicated(keep=selected_keep).sum()
            
            removed_rows = len(df) - remaining_rows
            
            st.metric("Total Rows", remaining_rows)
            st.metric("Rows Removed", removed_rows)
            st.metric("Reduction", f"{(removed_rows / len(df) * 100):.2f}%" if len(df) > 0 else "0%")
    
    except Exception as e:
        st.error(f"Error in preview: {str(e)}")
        return None
    
    # Apply button
    if st.button("Remove Duplicates", type="primary"):
        try:
            processed_df = DataProcessor.remove_duplicates(
                df, 
                subset=selected_columns, 
                keep=selected_keep
            )
            
            # Show results
            original_count = len(df)
            new_count = len(processed_df)
            removed_count = original_count - new_count
            
            st.success(f"✅ Duplicates removed successfully!")
            st.info(f"Removed {removed_count} duplicate rows ({(removed_count/original_count*100):.2f}%)")
            
            return processed_df
            
        except Exception as e:
            st.error(f"Error removing duplicates: {str(e)}")
            return None
    
    return None


def show_advanced_duplicate_analysis(df: pd.DataFrame) -> None:
    """Show advanced duplicate analysis with detailed insights."""
    
    st.subheader("🔬 Advanced Duplicate Analysis")
    
    # Column selection for analysis
    selected_cols = st.multiselect(
        "Select columns for detailed analysis:",
        options=list(df.columns),
        default=list(df.columns)[:5] if len(df.columns) > 5 else list(df.columns),
        key="advanced_duplicate_cols"
    )
    
    if not selected_cols:
        st.warning("Please select at least one column for analysis.")
        return
    
    # Analyze duplicates for selected columns
    duplicate_info = DataProcessor.detect_duplicates(df, selected_cols)
    
    if duplicate_info['total_duplicates'] == 0:
        st.success("No duplicates found for selected columns.")
        return
    
    # Detailed duplicate groups analysis
    st.write("**Detailed Duplicate Groups:**")
    
    if duplicate_info['duplicate_groups']:
        # Create expandable sections for each duplicate group
        for i, (group_key, group_info) in enumerate(duplicate_info['duplicate_groups'].items()):
            if i >= 10:  # Limit to first 10 groups
                st.info(f"Showing first 10 of {len(duplicate_info['duplicate_groups'])} duplicate groups")
                break
            
            with st.expander(f"Group {i+1}: {group_key[:100]}... ({group_info['count']} rows)"):
                # Get the actual rows for this group
                group_indices = group_info['indices']
                group_rows = df.loc[group_indices]
                
                st.write(f"**Indices:** {group_indices}")
                st.write(f"**First occurrence:** {group_info['first_occurrence']}")
                
                # Show the duplicate rows
                st.dataframe(group_rows, use_container_width=True)
                
                # Show differences between rows (if any)
                if len(group_rows) > 1:
                    st.write("**Differences between duplicate rows:**")
                    
                    # Check which columns have different values
                    diff_cols = []
                    for col in df.columns:
                        if col not in selected_cols:  # Only check non-key columns
                            unique_vals = group_rows[col].nunique()
                            if unique_vals > 1:
                                diff_cols.append(col)
                    
                    if diff_cols:
                        st.write(f"Columns with differences: {', '.join(diff_cols)}")
                        diff_df = group_rows[diff_cols]
                        st.dataframe(diff_df, use_container_width=True)
                    else:
                        st.info("All rows are identical")
    
    # Duplicate patterns analysis
    st.write("**Duplicate Patterns:**")
    
    # Analyze which combinations of columns have the most duplicates
    pattern_analysis = []
    
    for i in range(1, min(4, len(selected_cols) + 1)):  # Check combinations up to 3 columns
        from itertools import combinations
        
        for col_combo in combinations(selected_cols, i):
            combo_duplicates = DataProcessor.detect_duplicates(df, list(col_combo))
            if combo_duplicates['total_duplicates'] > 0:
                pattern_analysis.append({
                    'Columns': ', '.join(col_combo),
                    'Duplicate Count': combo_duplicates['total_duplicates'],
                    'Duplicate %': combo_duplicates['duplicate_percentage']
                })
    
    if pattern_analysis:
        pattern_df = pd.DataFrame(pattern_analysis)
        pattern_df = pattern_df.sort_values('Duplicate Count', ascending=False)
        st.dataframe(
            pattern_df.style.format({'Duplicate %': '{:.2f}%'}),
            use_container_width=True
        )
    else:
        st.info("No duplicate patterns found for selected columns.")