"""
Unit tests for data models
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from core.models import Dataset, AnalysisResult, VisualizationConfig


class TestDataset:
    """Test cases for Dataset model."""
    
    def setup_method(self):
        """Set up test data."""
        self.test_data = pd.DataFrame({
            'numeric_col': [1, 2, 3, 4, 5],
            'categorical_col': ['A', 'B', 'A', 'C', 'B'],
            'missing_col': [1, None, 3, None, 5]
        })
        
        self.dataset = Dataset(
            name="test_dataset",
            data=self.test_data
        )
    
    def test_dataset_initialization(self):
        """Test dataset initialization."""
        assert self.dataset.name == "test_dataset"
        assert self.dataset.data.equals(self.test_data)
        assert isinstance(self.dataset.metadata, dict)
        assert 'created_at' in self.dataset.metadata
        assert 'original_shape' in self.dataset.metadata
        assert self.dataset.metadata['original_shape'] == (5, 3)
    
    def test_get_summary(self):
        """Test dataset summary generation."""
        summary = self.dataset.get_summary()
        
        assert summary['name'] == "test_dataset"
        assert summary['shape'] == (5, 3)
        assert len(summary['columns']) == 3
        assert 'numeric_col' in summary['columns']
        assert summary['missing_values']['missing_col'] == 2
        assert summary['is_cleaned'] == False
    
    def test_get_column_info(self):
        """Test column information generation."""
        column_info = self.dataset.get_column_info()
        
        # Test numeric column
        numeric_info = column_info['numeric_col']
        assert numeric_info['dtype'] == 'int64'
        assert numeric_info['null_count'] == 0
        assert numeric_info['unique_count'] == 5
        assert 'mean' in numeric_info
        assert numeric_info['mean'] == 3.0
        
        # Test categorical column
        cat_info = column_info['categorical_col']
        assert cat_info['unique_count'] == 3
        assert 'mean' not in cat_info  # Should not have numeric stats
        
        # Test column with missing values
        missing_info = column_info['missing_col']
        assert missing_info['null_count'] == 2
        assert missing_info['null_percentage'] == 40.0
    
    def test_cleaning_operations(self):
        """Test cleaning operation tracking."""
        assert not self.dataset.is_cleaned()
        
        self.dataset.add_cleaning_operation("Removed duplicates")
        assert self.dataset.is_cleaned()
        assert len(self.dataset.cleaning_history) == 1
        assert "Removed duplicates" in self.dataset.cleaning_history[0]
        
        self.dataset.add_cleaning_operation("Filled missing values")
        assert len(self.dataset.cleaning_history) == 2


class TestAnalysisResult:
    """Test cases for AnalysisResult model."""
    
    def setup_method(self):
        """Set up test data."""
        self.result = AnalysisResult(
            dataset_name="test_dataset",
            analysis_type="descriptive_stats",
            results={"mean": 3.0, "std": 1.58},
            parameters={"method": "standard"}
        )
    
    def test_analysis_result_initialization(self):
        """Test analysis result initialization."""
        assert self.result.dataset_name == "test_dataset"
        assert self.result.analysis_type == "descriptive_stats"
        assert self.result.results["mean"] == 3.0
        assert isinstance(self.result.timestamp, datetime)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        result_dict = self.result.to_dict()
        
        assert result_dict['dataset_name'] == "test_dataset"
        assert result_dict['analysis_type'] == "descriptive_stats"
        assert result_dict['results']['mean'] == 3.0
        assert 'timestamp' in result_dict
        assert result_dict['parameters']['method'] == "standard"
    
    def test_export_to_json(self):
        """Test JSON export."""
        json_str = self.result.export_to_json()
        
        assert isinstance(json_str, str)
        assert "test_dataset" in json_str
        assert "descriptive_stats" in json_str
        assert "3.0" in json_str


class TestVisualizationConfig:
    """Test cases for VisualizationConfig model."""
    
    def test_valid_single_column_config(self):
        """Test valid single column configuration."""
        config = VisualizationConfig(
            chart_type="histogram",
            columns=["numeric_col"]
        )
        
        assert config.validate()
        assert config.chart_type == "histogram"
        assert len(config.columns) == 1
        assert config.styling['height'] == 400
    
    def test_valid_multi_column_config(self):
        """Test valid multi-column configuration."""
        config = VisualizationConfig(
            chart_type="scatter_plot",
            columns=["col1", "col2"]
        )
        
        assert config.validate()
        assert config.chart_type == "scatter_plot"
        assert len(config.columns) == 2
    
    def test_invalid_chart_type(self):
        """Test invalid chart type."""
        config = VisualizationConfig(
            chart_type="invalid_chart",
            columns=["col1"]
        )
        
        assert not config.validate()
    
    def test_invalid_column_count(self):
        """Test invalid column count for chart type."""
        # Single column chart with multiple columns
        config1 = VisualizationConfig(
            chart_type="histogram",
            columns=["col1", "col2"]
        )
        assert not config1.validate()
        
        # Multi-column chart with single column
        config2 = VisualizationConfig(
            chart_type="scatter_plot",
            columns=["col1"]
        )
        assert not config2.validate()
    
    def test_plotly_config_generation(self):
        """Test Plotly configuration generation."""
        config = VisualizationConfig(
            chart_type="histogram",
            columns=["col1"]
        )
        
        plotly_config = config.to_plotly_config()
        
        assert 'displayModeBar' in plotly_config
        assert plotly_config['displaylogo'] == False
        assert 'toImageButtonOptions' in plotly_config
        assert plotly_config['toImageButtonOptions']['format'] == 'png'


if __name__ == "__main__":
    pytest.main([__file__])