"""
Simple test to verify the app can be imported and basic functionality works
"""

def test_imports():
    """Test that all modules can be imported."""
    try:
        # Test core imports
        from core.models import Dataset, AnalysisResult, VisualizationConfig
        from core.session_manager import SessionStateManager
        from core.data_processor import DataProcessor
        
        # Test page imports
        from pages import preprocessing, analysis, requirements
        
        # Test utils
        from utils.missing_value_ui import show_missing_value_analysis
        from utils.duplicate_ui import show_duplicate_analysis
        
        # Test config
        from config.settings import MAX_FILE_SIZE_MB
        
        print("✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without Streamlit."""
    import pandas as pd
    from core.models import Dataset
    from core.data_processor import DataProcessor
    
    try:
        # Create test data
        test_df = pd.DataFrame({
            'numeric_col': [1, 2, 3, None, 5],
            'categorical_col': ['A', 'B', 'A', 'C', None],
            'complete_col': [1, 2, 3, 4, 5]
        })
        
        # Test Dataset creation
        dataset = Dataset(name="test", data=test_df)
        summary = dataset.get_summary()
        assert summary['name'] == "test"
        assert summary['shape'] == (5, 3)
        
        # Test missing value detection
        missing_info = DataProcessor.detect_missing_values(test_df)
        assert missing_info['total_missing'] == 2
        
        # Test missing value handling
        cleaned_df = DataProcessor.handle_missing_values(test_df, 'drop')
        assert cleaned_df.shape[0] == 3  # Should have 3 rows after dropping missing
        
        # Test duplicate detection and removal
        dup_df = pd.DataFrame({
            'col1': [1, 2, 1, 3],
            'col2': ['A', 'B', 'A', 'C']
        })
        
        duplicate_info = DataProcessor.detect_duplicates(dup_df)
        assert duplicate_info['total_duplicates'] == 1  # One duplicate row
        
        cleaned_dup_df = DataProcessor.remove_duplicates(dup_df)
        assert cleaned_dup_df.shape[0] == 3  # Should have 3 rows after removing duplicates
        
        print("✅ Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

if __name__ == "__main__":
    print("Testing EDA Automation Tool...")
    
    import_success = test_imports()
    func_success = test_basic_functionality()
    
    if import_success and func_success:
        print("\n🎉 All tests passed! The app should work correctly.")
        print("\nTo run the app:")
        print("streamlit run app.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")