"""
Requirements page for EDA Automation Tool
Shows documentation, usage instructions, and system requirements.
"""

import streamlit as st
import pandas as pd
import sys
import platform
from config.settings import SUPPORTED_FILE_TYPES, MAX_FILE_SIZE_MB


def show():
    """Display the requirements page."""
    
    st.title("📋 Requirements & Documentation")
    st.markdown("Learn how to use the EDA Automation Tool and check system requirements.")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📖 User Guide", "⚙️ System Info", "🔧 Features", "❓ FAQ"])
    
    with tab1:
        show_user_guide()
    
    with tab2:
        show_system_info()
    
    with tab3:
        show_features()
    
    with tab4:
        show_faq()


def show_user_guide():
    """Show user guide and instructions."""
    
    st.subheader("📖 User Guide")
    
    st.markdown("""
    ## Welcome to EDA Automation Tool!
    
    This tool helps you perform exploratory data analysis quickly and efficiently. Follow these steps to get started:
    
    ### 🚀 Getting Started
    
    1. **Upload Your Data** (Preprocessing Page)
       - Click on the "Preprocessing" tab in the sidebar
       - Upload your dataset using the file uploader
       - Supported formats: CSV, Excel (.xlsx, .xls), JSON
       - Maximum file size: 200MB
    
    2. **Clean Your Data** (Preprocessing Page)
       - Review the data preview and column information
       - Handle missing values using various strategies
       - Remove duplicate rows if needed
       - Convert data types automatically
       - Detect and remove outliers
    
    3. **Analyze Your Data** (Analysis Page)
       - View descriptive statistics for all variables
       - Explore individual variables with univariate analysis
       - Discover relationships between variables
       - Generate correlation matrices and scatter plots
    
    ### 📊 Data Preprocessing Features
    
    #### Missing Value Handling
    - **Drop**: Remove rows with missing values
    - **Mean/Median**: Fill numeric missing values with mean or median
    - **Mode**: Fill categorical missing values with most frequent value
    - **Forward/Backward Fill**: Use adjacent values to fill missing data
    - **Constant**: Fill with a constant value (0 for numeric, 'Unknown' for text)
    
    #### Duplicate Detection
    - Automatically detect duplicate rows
    - View duplicate records before removal
    - One-click duplicate removal
    
    #### Data Type Conversion
    - Automatic detection of numeric and datetime columns
    - Convert text columns to appropriate data types
    - Preview changes before applying
    
    #### Outlier Detection
    - Uses Interquartile Range (IQR) method
    - Identifies values beyond 1.5 × IQR from Q1 and Q3
    - Option to remove outlier rows
    
    ### 📈 Analysis Features
    
    #### Descriptive Statistics
    - **Central Tendency**: Mean, median, mode
    - **Dispersion**: Standard deviation, variance, range, IQR
    - **Shape**: Skewness and kurtosis
    - **Data Quality**: Completeness and uniqueness metrics
    
    #### Univariate Analysis
    - **Numeric Variables**: Histograms, box plots, Q-Q plots
    - **Categorical Variables**: Bar charts, pie charts, value counts
    - **Statistical Summaries**: Comprehensive statistics for each variable
    
    #### Bivariate Analysis
    - **Correlation Analysis**: Pearson correlation matrix with heatmap
    - **Scatter Plots**: Interactive plots with trend lines
    - **Strong Correlation Detection**: Automatically identify correlations > 0.7
    
    ### 💡 Tips for Best Results
    
    1. **Data Quality**: Clean your data thoroughly before analysis
    2. **Missing Values**: Choose appropriate strategies based on data type and missing percentage
    3. **Outliers**: Consider the context before removing outliers
    4. **Correlations**: Strong correlations don't imply causation
    5. **Sample Size**: Ensure adequate sample size for reliable statistics
    """)


def show_system_info():
    """Show system information and requirements."""
    
    st.subheader("⚙️ System Information")
    
    # Current system info
    st.write("**Current System:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Python Version:** {sys.version.split()[0]}")
        st.info(f"**Platform:** {platform.system()} {platform.release()}")
        st.info(f"**Architecture:** {platform.machine()}")
    
    with col2:
        st.info(f"**Streamlit Version:** {st.__version__}")
        st.info(f"**Pandas Version:** {pd.__version__}")
    
    # Requirements
    st.write("**System Requirements:**")
    
    requirements = {
        "Python": "≥ 3.8",
        "RAM": "≥ 4GB (8GB recommended)",
        "Storage": "≥ 100MB free space",
        "Browser": "Chrome, Firefox, Safari, Edge (latest versions)"
    }
    
    req_df = pd.DataFrame(list(requirements.items()), columns=['Component', 'Requirement'])
    st.dataframe(req_df, use_container_width=True, hide_index=True)
    
    # File specifications
    st.write("**File Specifications:**")
    
    file_specs = {
        "Supported Formats": ", ".join(SUPPORTED_FILE_TYPES).upper(),
        "Maximum File Size": f"{MAX_FILE_SIZE_MB} MB",
        "Maximum Rows": "No hard limit (depends on available RAM)",
        "Maximum Columns": "No hard limit",
        "Encoding": "UTF-8, Latin-1 (auto-detected)"
    }
    
    spec_df = pd.DataFrame(list(file_specs.items()), columns=['Specification', 'Value'])
    st.dataframe(spec_df, use_container_width=True, hide_index=True)
    
    # Dependencies
    st.write("**Key Dependencies:**")
    
    dependencies = [
        "streamlit ≥ 1.28.0",
        "pandas ≥ 2.0.0",
        "numpy ≥ 1.24.0",
        "plotly ≥ 5.15.0",
        "seaborn ≥ 0.12.0",
        "scipy ≥ 1.10.0",
        "openpyxl ≥ 3.1.0",
        "scikit-learn ≥ 1.3.0"
    ]
    
    for dep in dependencies:
        st.code(dep)


def show_features():
    """Show detailed feature list."""
    
    st.subheader("🔧 Features Overview")
    
    # Data Processing Features
    st.write("### 📁 Data Loading & Processing")
    
    processing_features = [
        "✅ Multi-format file support (CSV, Excel, JSON)",
        "✅ Automatic encoding detection",
        "✅ File validation and error handling",
        "✅ Data preview with sample rows",
        "✅ Column information and data types",
        "✅ Memory usage optimization"
    ]
    
    for feature in processing_features:
        st.markdown(feature)
    
    # Cleaning Features
    st.write("### 🧹 Data Cleaning")
    
    cleaning_features = [
        "✅ Missing value detection and analysis",
        "✅ Multiple imputation strategies",
        "✅ Duplicate row detection and removal",
        "✅ Automatic data type conversion",
        "✅ Outlier detection (IQR method)",
        "✅ Data cleaning history tracking"
    ]
    
    for feature in cleaning_features:
        st.markdown(feature)
    
    # Analysis Features
    st.write("### 📊 Statistical Analysis")
    
    analysis_features = [
        "✅ Descriptive statistics (mean, median, mode, std, etc.)",
        "✅ Data quality metrics (completeness, uniqueness)",
        "✅ Distribution analysis (skewness, kurtosis)",
        "✅ Correlation analysis with heatmaps",
        "✅ Univariate analysis with visualizations",
        "✅ Bivariate analysis with scatter plots"
    ]
    
    for feature in analysis_features:
        st.markdown(feature)
    
    # Visualization Features
    st.write("### 📈 Visualizations")
    
    viz_features = [
        "✅ Interactive histograms and box plots",
        "✅ Bar charts and pie charts for categories",
        "✅ Correlation heatmaps",
        "✅ Scatter plots with trend lines",
        "✅ Q-Q plots for normality assessment",
        "✅ Responsive and downloadable charts"
    ]
    
    for feature in viz_features:
        st.markdown(feature)
    
    # UI Features
    st.write("### 🖥️ User Interface")
    
    ui_features = [
        "✅ Intuitive three-page navigation",
        "✅ Real-time data preview",
        "✅ Progress indicators and status updates",
        "✅ Error handling with helpful messages",
        "✅ Session state management",
        "✅ Responsive design for different screen sizes"
    ]
    
    for feature in ui_features:
        st.markdown(feature)


def show_faq():
    """Show frequently asked questions."""
    
    st.subheader("❓ Frequently Asked Questions")
    
    faqs = [
        {
            "question": "What file formats are supported?",
            "answer": "The tool supports CSV, Excel (.xlsx, .xls), and JSON files. Files are automatically parsed with encoding detection."
        },
        {
            "question": "What's the maximum file size I can upload?",
            "answer": f"The maximum file size is {MAX_FILE_SIZE_MB}MB. For larger files, consider sampling or splitting your data."
        },
        {
            "question": "How should I handle missing values?",
            "answer": "The choice depends on your data:\n- **< 5% missing**: Usually safe to drop rows\n- **5-30% missing**: Consider imputation (mean/median for numeric, mode for categorical)\n- **> 30% missing**: Consider dropping the column or collecting more data"
        },
        {
            "question": "What does the correlation analysis show?",
            "answer": "Correlation analysis shows linear relationships between numeric variables. Values range from -1 to 1:\n- **> 0.7**: Strong positive correlation\n- **< -0.7**: Strong negative correlation\n- **Near 0**: No linear relationship"
        },
        {
            "question": "How are outliers detected?",
            "answer": "Outliers are detected using the Interquartile Range (IQR) method. Values below Q1 - 1.5×IQR or above Q3 + 1.5×IQR are considered outliers."
        },
        {
            "question": "Can I reset my data to the original version?",
            "answer": "Yes! The tool keeps a copy of your original data. Use the 'Reset to Original Data' button on the Preprocessing page."
        },
        {
            "question": "Why can't I see the Analysis page?",
            "answer": "You need to upload a dataset first. Go to the Preprocessing page and upload your data file."
        },
        {
            "question": "How do I interpret skewness and kurtosis?",
            "answer": "**Skewness** measures asymmetry:\n- **0**: Symmetric distribution\n- **> 0**: Right-skewed (tail extends right)\n- **< 0**: Left-skewed (tail extends left)\n\n**Kurtosis** measures tail heaviness:\n- **3**: Normal distribution\n- **> 3**: Heavy tails (more outliers)\n- **< 3**: Light tails (fewer outliers)"
        },
        {
            "question": "What should I do if my data won't load?",
            "answer": "Check these common issues:\n- File format is supported (CSV, Excel, JSON)\n- File size is under the limit\n- File is not corrupted\n- CSV files have proper delimiters\n- Excel files are not password protected"
        },
        {
            "question": "How can I export my results?",
            "answer": "Currently, you can:\n- Download individual charts by hovering over them and clicking the download icon\n- Copy statistics tables\n- Take screenshots of the analysis\n\nFull export functionality is planned for future versions."
        }
    ]
    
    for i, faq in enumerate(faqs):
        with st.expander(f"**{faq['question']}**"):
            st.markdown(faq['answer'])
    
    # Contact/Support section
    st.markdown("---")
    st.write("### 📞 Need More Help?")
    st.info("""
    If you have additional questions or encounter issues:
    
    1. **Check the User Guide** above for detailed instructions
    2. **Review error messages** carefully - they often contain helpful information
    3. **Try with a smaller dataset** to isolate issues
    4. **Ensure your data is properly formatted** before upload
    
    Remember: This tool is designed to help with exploratory data analysis. For advanced statistical modeling or machine learning, consider using specialized tools like R, Python with scikit-learn, or dedicated statistical software.
    """)