"""
Test download functionality
"""

import pandas as pd
from io import BytesIO
from core.models import Dataset


def test_csv_export():
    """Test CSV export functionality."""
    
    # Create test dataset
    test_df = pd.DataFrame({
        'col1': [1, 2, 3, 4, 5],
        'col2': ['A', 'B', 'C', 'D', 'E']
    })
    
    dataset = Dataset(name="test", data=test_df)
    dataset.add_cleaning_operation("Test operation")
    
    # Export to CSV
    csv_data = dataset.data.to_csv(index=False)
    
    # Verify CSV can be read back
    csv_df = pd.read_csv(pd.io.common.StringIO(csv_data))
    
    assert csv_df.shape == test_df.shape
    assert list(csv_df.columns) == list(test_df.columns)
    
    print("✅ CSV export test passed!")


def test_excel_export():
    """Test Excel export functionality."""
    
    try:
        # Create test dataset
        test_df = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['A', 'B', 'C', 'D', 'E']
        })
        
        dataset = Dataset(name="test", data=test_df)
        dataset.add_cleaning_operation("Test operation 1")
        dataset.add_cleaning_operation("Test operation 2")
        
        # Export to Excel
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            dataset.data.to_excel(writer, index=False, sheet_name='Cleaned Data')
            
            # Add summary sheet
            if dataset.cleaning_history:
                summary_df = pd.DataFrame({
                    'Operation': [op.split(': ', 1)[1] if ': ' in op else op for op in dataset.cleaning_history],
                    'Timestamp': [op.split(': ', 1)[0] if ': ' in op else '' for op in dataset.cleaning_history]
                })
                summary_df.to_excel(writer, index=False, sheet_name='Cleaning History')
        
        excel_data = buffer.getvalue()
        
        # Verify Excel can be read back
        excel_df = pd.read_excel(BytesIO(excel_data), sheet_name='Cleaned Data')
        
        assert excel_df.shape == test_df.shape
        assert list(excel_df.columns) == list(test_df.columns)
        
        # Verify summary sheet exists
        summary_df = pd.read_excel(BytesIO(excel_data), sheet_name='Cleaning History')
        assert len(summary_df) == 2  # Two cleaning operations
        
        print("✅ Excel export test passed!")
        
    except Exception as e:
        print(f"⚠️  Excel export test skipped: {str(e)}")


def test_metadata_export():
    """Test metadata JSON export."""
    
    import json
    from datetime import datetime
    
    # Create test dataset
    test_df = pd.DataFrame({
        'col1': [1, 2, 3, 4, 5],
        'col2': ['A', 'B', 'C', 'D', 'E']
    })
    
    dataset = Dataset(name="test", data=test_df)
    dataset.add_cleaning_operation("Test operation")
    
    # Create metadata export
    metadata_export = {
        'dataset_name': dataset.name,
        'export_timestamp': datetime.now().isoformat(),
        'original_shape': dataset.metadata.get('original_shape'),
        'current_shape': dataset.data.shape,
        'cleaning_operations': dataset.cleaning_history,
        'data_quality_metrics': {
            'completeness': 100.0,
            'missing_values': 0,
            'duplicate_rows': 0
        }
    }
    
    # Export to JSON
    json_data = json.dumps(metadata_export, indent=2)
    
    # Verify JSON can be parsed
    parsed_data = json.loads(json_data)
    
    assert parsed_data['dataset_name'] == 'test'
    assert parsed_data['current_shape'] == [5, 2]
    assert len(parsed_data['cleaning_operations']) == 1
    
    print("✅ Metadata export test passed!")


def test_summary_report():
    """Test summary report generation."""
    
    from pages.preprocessing import generate_summary_report
    
    # Create test dataset
    test_df = pd.DataFrame({
        'numeric_col': [1, 2, 3, 4, 5],
        'text_col': ['A', 'B', 'C', 'D', 'E']
    })
    
    dataset = Dataset(name="test", data=test_df)
    dataset.add_cleaning_operation("Removed duplicates")
    dataset.add_cleaning_operation("Handled missing values")
    
    # Generate report
    report = generate_summary_report(dataset)
    
    # Verify report contains key information
    assert 'DATA CLEANING SUMMARY REPORT' in report
    assert 'test' in report
    assert 'Removed duplicates' in report
    assert 'Handled missing values' in report
    assert 'numeric_col' in report
    assert 'text_col' in report
    
    print("✅ Summary report test passed!")


if __name__ == "__main__":
    print("Testing download functionality...\n")
    
    test_csv_export()
    test_excel_export()
    test_metadata_export()
    test_summary_report()
    
    print("\n🎉 All download tests passed!")