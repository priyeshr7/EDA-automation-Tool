"""
Data models for EDA Automation Tool
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.graph_objects as go


@dataclass
class Dataset:
    """Dataset model with metadata and quality metrics tracking."""
    
    name: str
    data: pd.DataFrame
    metadata: Dict[str, Any] = field(default_factory=dict)
    cleaning_history: List[str] = field(default_factory=list)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize metadata after object creation."""
        if not self.metadata:
            self.metadata = {
                'created_at': datetime.now(),
                'original_shape': self.data.shape,
                'file_size_mb': round(self.data.memory_usage(deep=True).sum() / 1024**2, 2)
            }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get dataset summary information."""
        return {
            'name': self.name,
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'memory_usage_mb': self.metadata.get('file_size_mb', 0),
            'cleaning_operations': len(self.cleaning_history),
            'is_cleaned': self.is_cleaned()
        }
    
    def get_column_info(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed information about each column."""
        column_info = {}
        
        for col in self.data.columns:
            col_data = self.data[col]
            info = {
                'dtype': str(col_data.dtype),
                'non_null_count': col_data.count(),
                'null_count': col_data.isnull().sum(),
                'null_percentage': round((col_data.isnull().sum() / len(col_data)) * 100, 2),
                'unique_count': col_data.nunique(),
                'unique_percentage': round((col_data.nunique() / len(col_data)) * 100, 2)
            }
            
            # Add numeric-specific info
            if pd.api.types.is_numeric_dtype(col_data):
                info.update({
                    'mean': col_data.mean() if col_data.count() > 0 else None,
                    'std': col_data.std() if col_data.count() > 0 else None,
                    'min': col_data.min() if col_data.count() > 0 else None,
                    'max': col_data.max() if col_data.count() > 0 else None,
                    'median': col_data.median() if col_data.count() > 0 else None
                })
            
            column_info[col] = info
        
        return column_info
    
    def is_cleaned(self) -> bool:
        """Check if dataset has been cleaned."""
        return len(self.cleaning_history) > 0
    
    def add_cleaning_operation(self, operation: str) -> None:
        """Add a cleaning operation to history."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cleaning_history.append(f"{timestamp}: {operation}")


@dataclass
class AnalysisResult:
    """Analysis result model with metadata."""
    
    dataset_name: str
    analysis_type: str
    results: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis result to dictionary."""
        return {
            'dataset_name': self.dataset_name,
            'analysis_type': self.analysis_type,
            'results': self.results,
            'timestamp': self.timestamp.isoformat(),
            'parameters': self.parameters
        }
    
    def export_to_json(self) -> str:
        """Export analysis result to JSON string."""
        import json
        return json.dumps(self.to_dict(), indent=2, default=str)


@dataclass
class VisualizationConfig:
    """Visualization configuration model."""
    
    chart_type: str
    columns: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    styling: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default styling."""
        if not self.styling:
            self.styling = {
                'height': 400,
                'width': 600,
                'color_palette': 'viridis',
                'show_legend': True,
                'title_size': 16,
                'axis_label_size': 12
            }
    
    def validate(self) -> bool:
        """Validate visualization configuration."""
        if not self.chart_type:
            return False
        
        if not self.columns:
            return False
        
        # Chart-specific validation
        valid_chart_types = [
            'histogram', 'box_plot', 'violin_plot', 'bar_chart', 'pie_chart',
            'scatter_plot', 'correlation_heatmap', 'pair_plot', 'line_plot'
        ]
        
        if self.chart_type not in valid_chart_types:
            return False
        
        # Column count validation
        single_column_charts = ['histogram', 'box_plot', 'violin_plot', 'bar_chart', 'pie_chart']
        multi_column_charts = ['scatter_plot', 'correlation_heatmap', 'pair_plot']
        
        if self.chart_type in single_column_charts and len(self.columns) != 1:
            return False
        
        if self.chart_type in multi_column_charts and len(self.columns) < 2:
            return False
        
        return True
    
    def to_plotly_config(self) -> Dict[str, Any]:
        """Convert to Plotly configuration dictionary."""
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': f'{self.chart_type}_chart',
                'height': self.styling.get('height', 400),
                'width': self.styling.get('width', 600),
                'scale': 2
            }
        }
        
        return config