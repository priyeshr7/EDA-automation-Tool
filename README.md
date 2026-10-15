# EDA Automation Tool

A comprehensive Streamlit web application for automated Exploratory Data Analysis (EDA). This tool streamlines the data analysis workflow by automating data cleaning, statistical analysis, and visualization tasks.

## 🚀 Features

### 📁 Data Loading & Processing
- **Multi-format Support**: CSV, Excel (.xlsx, .xls), JSON
- **Automatic Encoding Detection**: Handles various text encodings
- **File Validation**: Size limits and format checking
- **Data Preview**: Sample rows and column information
- **Memory Optimization**: Efficient handling of large datasets

### 🧹 Data Cleaning
- **Missing Value Handling**: Multiple imputation strategies
  - Drop rows/columns
  - Fill with mean, median, mode
  - Forward/backward fill
  - Constant value imputation
- **Duplicate Detection**: Identify and remove duplicate rows
- **Data Type Conversion**: Automatic type inference and conversion
- **Outlier Detection**: IQR-based outlier identification and removal
- **Cleaning History**: Track all data cleaning operations

### 📊 Statistical Analysis
- **Descriptive Statistics**: Mean, median, mode, standard deviation, variance, range, IQR
- **Distribution Analysis**: Skewness, kurtosis, normality assessment
- **Data Quality Metrics**: Completeness, uniqueness, validity checks
- **Correlation Analysis**: Pearson correlation with heatmap visualization
- **Strong Correlation Detection**: Automatically identify correlations > 0.7

### 📈 Visualizations
- **Univariate Analysis**:
  - Histograms for numeric variables
  - Bar charts and pie charts for categorical variables
  - Box plots and Q-Q plots for distribution analysis
- **Bivariate Analysis**:
  - Scatter plots with trend lines
  - Correlation heatmaps
  - Interactive plotly charts

### 🖥️ User Interface
- **Three-Page Navigation**: Preprocessing, Analysis, Requirements
- **Session State Management**: Data persists across pages
- **Real-time Preview**: See changes before applying
- **Progress Indicators**: Visual feedback for operations
- **Responsive Design**: Works on different screen sizes

## 📋 Requirements

### System Requirements
- Python ≥ 3.8
- RAM ≥ 4GB (8GB recommended)
- Storage ≥ 100MB free space
- Modern web browser (Chrome, Firefox, Safari, Edge)

### File Specifications
- **Supported Formats**: CSV, XLSX, XLS, JSON
- **Maximum File Size**: 200MB
- **Encoding**: UTF-8, Latin-1 (auto-detected)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd eda-automation-tool
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

## 📖 Usage Guide

### 1. Upload Your Data
1. Go to the **Preprocessing** page
2. Click "Choose a file" and select your dataset
3. Supported formats: CSV, Excel, JSON
4. Review the data preview and column information

### 2. Clean Your Data
1. **Handle Missing Values**: Choose from multiple strategies
2. **Remove Duplicates**: One-click duplicate removal
3. **Convert Data Types**: Automatic type detection and conversion
4. **Detect Outliers**: IQR-based outlier identification

### 3. Analyze Your Data
1. Go to the **Analysis** page
2. View descriptive statistics for all variables
3. Explore individual variables with univariate analysis
4. Discover relationships with correlation analysis and scatter plots

### 4. Get Help
1. Visit the **Requirements** page for detailed documentation
2. Check the FAQ section for common questions
3. Review system requirements and feature descriptions

## 🏗️ Project Structure

```
eda-automation-tool/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── test_app.py           # Basic functionality tests
├── config/
│   ├── __init__.py
│   └── settings.py       # Application configuration
├── core/
│   ├── __init__.py
│   ├── models.py         # Data models (Dataset, AnalysisResult, etc.)
│   ├── session_manager.py # Session state management
│   └── data_processor.py # Data loading and processing
├── pages/
│   ├── __init__.py
│   ├── preprocessing.py  # Data preprocessing page
│   ├── analysis.py       # Statistical analysis page
│   └── requirements.py   # Documentation page
├── utils/
│   ├── __init__.py
│   └── missing_value_ui.py # UI components for missing values
└── tests/
    ├── __init__.py
    ├── test_models.py    # Tests for data models
    └── test_data_processor.py # Tests for data processing
```

## 🧪 Testing

Run the basic functionality test:
```bash
python test_app.py
```

Run unit tests:
```bash
python -m pytest tests/
```

## 📊 Example Workflows

### Basic EDA Workflow
1. Upload a CSV file with customer data
2. Handle missing values in age column using median imputation
3. Remove duplicate customer records
4. Analyze age distribution with histogram
5. Explore correlation between age and purchase amount
6. Generate scatter plot to visualize the relationship

### Data Quality Assessment
1. Upload dataset and review data preview
2. Check completeness and uniqueness metrics
3. Identify columns with high missing percentages
4. Detect and handle outliers in numeric columns
5. Validate data types and convert as needed

## 🔧 Configuration

Key settings can be modified in `config/settings.py`:

- `MAX_FILE_SIZE_MB`: Maximum upload file size (default: 200MB)
- `SUPPORTED_FILE_TYPES`: List of supported file formats
- `CORRELATION_THRESHOLD`: Threshold for strong correlations (default: 0.7)
- `DEFAULT_CHART_HEIGHT`: Default height for visualizations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the web interface
- Uses [Plotly](https://plotly.com/) for interactive visualizations
- Powered by [Pandas](https://pandas.pydata.org/) for data manipulation
- Statistical analysis with [SciPy](https://scipy.org/)

## 📞 Support

If you encounter any issues or have questions:

1. Check the **Requirements** page in the app for detailed documentation
2. Review the FAQ section for common solutions
3. Ensure your data is properly formatted
4. Try with a smaller dataset to isolate issues

---

**Happy Analyzing! 📊✨**