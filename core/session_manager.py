"""
Session State Manager for EDA Automation Tool
Manages application state across page navigation and user interactions.
"""

import streamlit as st
from typing import Any, Optional
from core.models import Dataset, AnalysisResult, VisualizationConfig


class SessionStateManager:
    """Manages Streamlit session state for cross-page data persistence."""
    
    @staticmethod
    def initialize_state() -> None:
        """Initialize session state with default values."""
        
        # Dataset management
        if 'dataset' not in st.session_state:
            st.session_state.dataset = None
        
        if 'original_dataset' not in st.session_state:
            st.session_state.original_dataset = None
        
        # Analysis results
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        
        # Visualization configs
        if 'visualization_configs' not in st.session_state:
            st.session_state.visualization_configs = []
        
        # User preferences
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {
                'missing_value_strategy': 'drop',
                'outlier_method': 'iqr',
                'correlation_method': 'pearson',
                'chart_theme': 'plotly',
                'auto_clean': False
            }
        
        # Processing flags
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
        
        if 'data_cleaned' not in st.session_state:
            st.session_state.data_cleaned = False
        
        if 'analysis_complete' not in st.session_state:
            st.session_state.analysis_complete = False
        
        # Cache for expensive operations
        if 'cached_stats' not in st.session_state:
            st.session_state.cached_stats = {}
        
        if 'cached_correlations' not in st.session_state:
            st.session_state.cached_correlations = {}
    
    @staticmethod
    def get_data(key: str) -> Any:
        """Get data from session state."""
        return st.session_state.get(key, None)
    
    @staticmethod
    def set_data(key: str, value: Any) -> None:
        """Set data in session state."""
        st.session_state[key] = value
    
    @staticmethod
    def clear_data(key: str) -> None:
        """Clear specific data from session state."""
        if key in st.session_state:
            del st.session_state[key]
    
    @staticmethod
    def is_data_loaded() -> bool:
        """Check if dataset is loaded."""
        return (st.session_state.get('data_loaded', False) and 
                st.session_state.get('dataset') is not None)
    
    @staticmethod
    def is_data_cleaned() -> bool:
        """Check if dataset has been cleaned."""
        return st.session_state.get('data_cleaned', False)
    
    @staticmethod
    def is_analysis_complete() -> bool:
        """Check if analysis has been completed."""
        return st.session_state.get('analysis_complete', False)
    
    @staticmethod
    def get_dataset() -> Optional[Dataset]:
        """Get current dataset."""
        return st.session_state.get('dataset')
    
    @staticmethod
    def set_dataset(dataset: Dataset) -> None:
        """Set current dataset and update flags."""
        st.session_state.dataset = dataset
        st.session_state.data_loaded = True
        
        # Keep original dataset for comparison
        if st.session_state.original_dataset is None:
            st.session_state.original_dataset = Dataset(
                name=f"{dataset.name}_original",
                data=dataset.data.copy(),
                metadata=dataset.metadata.copy()
            )
    
    @staticmethod
    def update_dataset(dataset: Dataset, operation: str) -> None:
        """Update dataset and add cleaning operation."""
        dataset.add_cleaning_operation(operation)
        st.session_state.dataset = dataset
        st.session_state.data_cleaned = True
        
        # Clear cached results that depend on data
        SessionStateManager.clear_cache()
    
    @staticmethod
    def add_analysis_result(result: AnalysisResult) -> None:
        """Add analysis result to session state."""
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        
        key = f"{result.analysis_type}_{result.timestamp.strftime('%Y%m%d_%H%M%S')}"
        st.session_state.analysis_results[key] = result
        st.session_state.analysis_complete = True
    
    @staticmethod
    def get_analysis_results() -> dict:
        """Get all analysis results."""
        return st.session_state.get('analysis_results', {})
    
    @staticmethod
    def add_visualization_config(config: VisualizationConfig) -> None:
        """Add visualization configuration."""
        if 'visualization_configs' not in st.session_state:
            st.session_state.visualization_configs = []
        
        st.session_state.visualization_configs.append(config)
    
    @staticmethod
    def get_visualization_configs() -> list:
        """Get all visualization configurations."""
        return st.session_state.get('visualization_configs', [])
    
    @staticmethod
    def get_user_preference(key: str, default: Any = None) -> Any:
        """Get user preference."""
        preferences = st.session_state.get('user_preferences', {})
        return preferences.get(key, default)
    
    @staticmethod
    def set_user_preference(key: str, value: Any) -> None:
        """Set user preference."""
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {}
        
        st.session_state.user_preferences[key] = value
    
    @staticmethod
    def cache_result(key: str, value: Any) -> None:
        """Cache expensive computation result."""
        cache_key = f"cached_{key}"
        if cache_key not in st.session_state:
            st.session_state[cache_key] = {}
        
        st.session_state[cache_key] = value
    
    @staticmethod
    def get_cached_result(key: str) -> Any:
        """Get cached computation result."""
        cache_key = f"cached_{key}"
        return st.session_state.get(cache_key)
    
    @staticmethod
    def clear_cache() -> None:
        """Clear all cached results."""
        cache_keys = [key for key in st.session_state.keys() if key.startswith('cached_')]
        for key in cache_keys:
            del st.session_state[key]
    
    @staticmethod
    def reset_session() -> None:
        """Reset entire session state."""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        SessionStateManager.initialize_state()
    
    @staticmethod
    def get_session_info() -> dict:
        """Get session information for debugging."""
        return {
            'data_loaded': SessionStateManager.is_data_loaded(),
            'data_cleaned': SessionStateManager.is_data_cleaned(),
            'analysis_complete': SessionStateManager.is_analysis_complete(),
            'dataset_shape': st.session_state.dataset.data.shape if st.session_state.get('dataset') else None,
            'analysis_count': len(SessionStateManager.get_analysis_results()),
            'visualization_count': len(SessionStateManager.get_visualization_configs()),
            'cache_keys': [key for key in st.session_state.keys() if key.startswith('cached_')]
        }