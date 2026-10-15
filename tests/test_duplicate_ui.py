"""
Unit tests for duplicate UI components
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from utils.duplicate_ui import show_duplicate_analysis, show_duplicate_handler, show_advanced_duplicate_analysis


class TestDuplicateUI:
    """Test cases for duplicate UI components."""
    
    def setup_method(self):
        """Set up test data."""
        self.df_no_duplicates = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['A', 'B', 'C', 'D', 'E'],
            'value': [10, 20, 30, 40, 50]
        })
        
        self.df_with_duplicates = pd.DataFrame({
            'id': [1, 2, 1, 3, 2],
            'name': ['A', 'B', 'A', 'C', 'B'],
            'value': [10, 20, 30, 40, 50]
        })
        
        self.df_partial_duplicates = pd.DataFrame({
            'id': [1, 2, 1, 3],
            'name': ['A', 'B', 'A', 'C'],
            'value': [10, 20, 30, 40]  # Different values for same id/name
        })
    
    @patch('streamlit.subheader')
    @patch('streamlit.success')
    def test_show_duplicate_analysis_no_duplicates(self, mock_success, mock_subheader):
        """Test duplicate analysis display with no duplicates."""
        
        # This would normally be called in Streamlit context
        # We're testing the logic without the actual UI
        from core.data_processor import DataProcessor
        
        duplicate_info = DataProcessor.detect_duplicates(self.df_no_duplicates)
        
        assert duplicate_info['total_duplicates'] == 0
        assert duplicate_info['duplicate_percentage'] == 0.0
        assert len(duplicate_info['duplicate_rows']) == 0
    
    @patch('streamlit.subheader')
    @patch('streamlit.metric')
    @patch('streamlit.dataframe')
    def test_show_duplicate_analysis_with_duplicates(self, mock_dataframe, mock_metric, mock_subheader):
        """Test duplicate analysis display with duplicates."""
        
        from core.data_processor import DataProcessor
        
        duplicate_info = DataProcessor.detect_duplicates(self.df_with_duplicates)
        
        assert duplicate_info['total_duplicates'] == 2
        assert duplicate_info['duplicate_percentage'] == 40.0
        assert len(duplicate_info['duplicate_rows']) == 4  # All rows involved in duplicates
        assert len(duplicate_info['duplicate_groups']) == 2
    
    def test_duplicate_removal_logic(self):
        """Test the logic behind duplicate removal without UI."""
        
        from core.data_processor import DataProcessor
        
        # Test keep='first'
        result_first = DataProcessor.remove_duplicates(self.df_with_duplicates, keep='first')
        assert len(result_first) == 3
        
        # Test keep='last'
        result_last = DataProcessor.remove_duplicates(self.df_with_duplicates, keep='last')
        assert len(result_last) == 3
        
        # Test keep=False (remove all duplicates)
        result_none = DataProcessor.remove_duplicates(self.df_with_duplicates, keep=False)
        assert len(result_none) == 1  # Only unique rows remain
    
    def test_duplicate_strategies_logic(self):
        """Test duplicate removal strategies logic."""
        
        from core.data_processor import DataProcessor
        
        strategies = DataProcessor.get_duplicate_removal_strategies(self.df_with_duplicates)
        
        assert 'keep_options' in strategies
        assert 'subset_options' in strategies
        assert 'column_suggestions' in strategies
        assert 'recommended_strategy' in strategies
        
        # Should have 3 keep options
        keep_options = strategies['keep_options']
        assert len(keep_options) == 3
        
        # Check that all expected options are present
        keep_values = [opt['value'] for opt in keep_options]
        assert 'first' in keep_values
        assert 'last' in keep_values
        assert False in keep_values
    
    def test_subset_duplicate_detection(self):
        """Test duplicate detection with column subsets."""
        
        from core.data_processor import DataProcessor
        
        # Detect duplicates based on id and name only
        duplicate_info = DataProcessor.detect_duplicates(
            self.df_partial_duplicates, 
            subset=['id', 'name']
        )
        
        assert duplicate_info['total_duplicates'] == 1  # One duplicate pair
        assert len(duplicate_info['duplicate_groups']) == 1
        
        # Remove duplicates based on subset
        result = DataProcessor.remove_duplicates(
            self.df_partial_duplicates, 
            subset=['id', 'name'], 
            keep='first'
        )
        
        assert len(result) == 3  # Should remove one row
        
        # Check that first occurrence is kept
        first_duplicate = result[result['id'] == 1]
        assert len(first_duplicate) == 1
        assert first_duplicate.iloc[0]['value'] == 10  # First occurrence value
    
    def test_column_analysis_logic(self):
        """Test column-wise duplicate analysis logic."""
        
        from core.data_processor import DataProcessor
        
        duplicate_info = DataProcessor.detect_duplicates(self.df_with_duplicates)
        col_analysis = duplicate_info['column_analysis']
        
        # Check that all columns are analyzed
        assert 'id' in col_analysis
        assert 'name' in col_analysis
        assert 'value' in col_analysis
        
        # Check analysis structure
        for col, analysis in col_analysis.items():
            assert 'duplicate_values' in analysis
            assert 'unique_values' in analysis
            assert 'duplicate_percentage' in analysis
            assert 'uniqueness_ratio' in analysis
            
            # Values should be reasonable
            assert analysis['duplicate_values'] >= 0
            assert analysis['unique_values'] >= 0
            assert 0 <= analysis['duplicate_percentage'] <= 100
            assert 0 <= analysis['uniqueness_ratio'] <= 100
    
    def test_error_handling(self):
        """Test error handling in duplicate detection."""
        
        from core.data_processor import DataProcessor
        
        # Test with invalid subset columns
        with pytest.raises(ValueError):
            DataProcessor.detect_duplicates(
                self.df_with_duplicates, 
                subset=['nonexistent_column']
            )
        
        with pytest.raises(ValueError):
            DataProcessor.remove_duplicates(
                self.df_with_duplicates, 
                subset=['nonexistent_column']
            )
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrames."""
        
        from core.data_processor import DataProcessor
        
        empty_df = pd.DataFrame()
        
        duplicate_info = DataProcessor.detect_duplicates(empty_df)
        
        assert duplicate_info['total_duplicates'] == 0
        assert duplicate_info['duplicate_percentage'] == 0
        assert len(duplicate_info['duplicate_rows']) == 0
        assert len(duplicate_info['duplicate_groups']) == 0
    
    def test_single_row_dataframe(self):
        """Test handling of single-row DataFrames."""
        
        from core.data_processor import DataProcessor
        
        single_row_df = pd.DataFrame({
            'col1': [1],
            'col2': ['A']
        })
        
        duplicate_info = DataProcessor.detect_duplicates(single_row_df)
        
        assert duplicate_info['total_duplicates'] == 0
        assert duplicate_info['duplicate_percentage'] == 0
        
        # Removal should return the same DataFrame
        result = DataProcessor.remove_duplicates(single_row_df)
        assert len(result) == 1
        assert result.equals(single_row_df)
    
    def test_all_identical_rows(self):
        """Test handling of DataFrames where all rows are identical."""
        
        from core.data_processor import DataProcessor
        
        identical_df = pd.DataFrame({
            'col1': [1, 1, 1, 1],
            'col2': ['A', 'A', 'A', 'A']
        })
        
        duplicate_info = DataProcessor.detect_duplicates(identical_df)
        
        assert duplicate_info['total_duplicates'] == 3  # 3 duplicate rows
        assert duplicate_info['duplicate_percentage'] == 75.0  # 3 out of 4
        
        # Keep first should result in 1 row
        result_first = DataProcessor.remove_duplicates(identical_df, keep='first')
        assert len(result_first) == 1
        
        # Keep none should result in 0 rows
        result_none = DataProcessor.remove_duplicates(identical_df, keep=False)
        assert len(result_none) == 0


if __name__ == "__main__":
    pytest.main([__file__])