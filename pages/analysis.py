"""
Analysis page for EDA Automation Tool
Handles statistical analysis and data visualization.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from core.session_manager import SessionStateManager
from core.models import Dataset


def show():
    """Display the analysis page."""
    
    st.title("📈 Data Analysis")
    st.markdown("Explore your data with automated statistical analysis and visualizations.")
    
    if not SessionStateManager.is_data_loaded():
        st.warning("⚠️ No data loaded. Please go to the Preprocessing page to upload a dataset.")
        return
    
    dataset = SessionStateManager.get_dataset()
    
    # Analysis sections
    show_dataset_overview(dataset)
    
    st.markdown("---")
    show_descriptive_statistics(dataset)
    
    st.markdown("---")
    show_univariate_analysis(dataset)
    
    st.markdown("---")
    show_bivariate_analysis(dataset)


def show_dataset_overview(dataset: Dataset):
    """Show dataset overview."""
    
    st.subheader("📊 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Rows", dataset.data.shape[0])
    
    with col2:
        st.metric("Columns", dataset.data.shape[1])
    
    with col3:
        missing_count = dataset.data.isnull().sum().sum()
        st.metric("Missing Values", missing_count)
    
    with col4:
        duplicate_count = dataset.data.duplicated().sum()
        st.metric("Duplicates", duplicate_count)
    
    # Data quality indicators
    st.write("**Data Quality Indicators:**")
    
    total_cells = dataset.data.shape[0] * dataset.data.shape[1]
    completeness = ((total_cells - missing_count) / total_cells) * 100
    uniqueness = ((dataset.data.shape[0] - duplicate_count) / dataset.data.shape[0]) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Completeness", f"{completeness:.2f}%")
    
    with col2:
        st.metric("Uniqueness", f"{uniqueness:.2f}%")


def show_descriptive_statistics(dataset: Dataset):
    """Show descriptive statistics."""
    
    st.subheader("📋 Descriptive Statistics")
    
    # Separate numeric and categorical columns
    numeric_cols = dataset.data.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = dataset.data.select_dtypes(include=['object', 'category']).columns.tolist()
    
    tab1, tab2 = st.tabs(["Numeric Variables", "Categorical Variables"])
    
    with tab1:
        if numeric_cols:
            st.write("**Summary Statistics for Numeric Variables:**")
            
            # Basic statistics
            desc_stats = dataset.data[numeric_cols].describe()
            st.dataframe(desc_stats, use_container_width=True)
            
            # Additional statistics
            st.write("**Additional Statistics:**")
            
            additional_stats = pd.DataFrame(index=numeric_cols)
            
            for col in numeric_cols:
                col_data = dataset.data[col].dropna()
                if len(col_data) > 0:
                    additional_stats.loc[col, 'Skewness'] = col_data.skew()
                    additional_stats.loc[col, 'Kurtosis'] = col_data.kurtosis()
                    additional_stats.loc[col, 'Variance'] = col_data.var()
                    additional_stats.loc[col, 'Range'] = col_data.max() - col_data.min()
                    additional_stats.loc[col, 'IQR'] = col_data.quantile(0.75) - col_data.quantile(0.25)
            
            st.dataframe(additional_stats.round(4), use_container_width=True)
            
        else:
            st.info("No numeric variables found in the dataset.")
    
    with tab2:
        if categorical_cols:
            st.write("**Summary for Categorical Variables:**")
            
            for col in categorical_cols:
                with st.expander(f"📊 {col}"):
                    col_data = dataset.data[col]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Unique Values", col_data.nunique())
                    
                    with col2:
                        st.metric("Most Frequent", col_data.mode().iloc[0] if not col_data.mode().empty else "N/A")
                    
                    with col3:
                        missing_count = col_data.isnull().sum()
                        st.metric("Missing", missing_count)
                    
                    # Value counts
                    st.write("**Value Counts:**")
                    value_counts = col_data.value_counts().head(10)
                    st.dataframe(value_counts, use_container_width=True)
        else:
            st.info("No categorical variables found in the dataset.")


def show_univariate_analysis(dataset: Dataset):
    """Show univariate analysis with visualizations."""
    
    st.subheader("📊 Univariate Analysis")
    
    # Column selection
    all_cols = dataset.data.columns.tolist()
    selected_col = st.selectbox("Select a variable to analyze:", all_cols)
    
    if selected_col:
        col_data = dataset.data[selected_col]
        
        # Basic info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Data Type", str(col_data.dtype))
        
        with col2:
            st.metric("Non-null Count", col_data.count())
        
        with col3:
            st.metric("Unique Values", col_data.nunique())
        
        # Visualization based on data type
        if pd.api.types.is_numeric_dtype(col_data):
            show_numeric_univariate_analysis(col_data, selected_col)
        else:
            show_categorical_univariate_analysis(col_data, selected_col)


def show_numeric_univariate_analysis(col_data: pd.Series, col_name: str):
    """Show analysis for numeric variables."""
    
    col_data_clean = col_data.dropna()
    
    if len(col_data_clean) == 0:
        st.warning("No valid data points for analysis.")
        return
    
    # Statistics
    st.write("**Statistics:**")
    stats_df = pd.DataFrame({
        'Statistic': ['Mean', 'Median', 'Mode', 'Std Dev', 'Variance', 'Skewness', 'Kurtosis', 'Min', 'Max', 'Range'],
        'Value': [
            col_data_clean.mean(),
            col_data_clean.median(),
            col_data_clean.mode().iloc[0] if not col_data_clean.mode().empty else np.nan,
            col_data_clean.std(),
            col_data_clean.var(),
            col_data_clean.skew(),
            col_data_clean.kurtosis(),
            col_data_clean.min(),
            col_data_clean.max(),
            col_data_clean.max() - col_data_clean.min()
        ]
    })
    
    st.dataframe(stats_df.round(4), use_container_width=True)
    
    # Visualizations
    st.write("**Visualizations:**")
    
    tab1, tab2, tab3 = st.tabs(["Histogram", "Box Plot", "Distribution"])
    
    with tab1:
        fig_hist = px.histogram(
            x=col_data_clean,
            nbins=30,
            title=f"Histogram of {col_name}",
            labels={'x': col_name, 'y': 'Frequency'}
        )
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with tab2:
        fig_box = px.box(
            y=col_data_clean,
            title=f"Box Plot of {col_name}",
            labels={'y': col_name}
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    with tab3:
        # Q-Q plot approximation using percentiles
        fig_qq = go.Figure()
        
        # Calculate percentiles
        percentiles = np.linspace(0.01, 0.99, 100)
        data_quantiles = np.percentile(col_data_clean, percentiles * 100)
        theoretical_quantiles = np.percentile(np.random.normal(col_data_clean.mean(), col_data_clean.std(), 10000), percentiles * 100)
        
        fig_qq.add_trace(go.Scatter(
            x=theoretical_quantiles,
            y=data_quantiles,
            mode='markers',
            name='Data vs Normal',
            marker=dict(size=4)
        ))
        
        # Add reference line
        min_val = min(theoretical_quantiles.min(), data_quantiles.min())
        max_val = max(theoretical_quantiles.max(), data_quantiles.max())
        fig_qq.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='Perfect Normal',
            line=dict(dash='dash', color='red')
        ))
        
        fig_qq.update_layout(
            title=f"Q-Q Plot: {col_name} vs Normal Distribution",
            xaxis_title="Theoretical Quantiles",
            yaxis_title="Sample Quantiles"
        )
        
        st.plotly_chart(fig_qq, use_container_width=True)


def show_categorical_univariate_analysis(col_data: pd.Series, col_name: str):
    """Show analysis for categorical variables."""
    
    col_data_clean = col_data.dropna()
    
    if len(col_data_clean) == 0:
        st.warning("No valid data points for analysis.")
        return
    
    # Value counts
    value_counts = col_data_clean.value_counts()
    
    st.write("**Value Counts:**")
    st.dataframe(value_counts, use_container_width=True)
    
    # Visualizations
    st.write("**Visualizations:**")
    
    tab1, tab2 = st.tabs(["Bar Chart", "Pie Chart"])
    
    with tab1:
        fig_bar = px.bar(
            x=value_counts.index,
            y=value_counts.values,
            title=f"Bar Chart of {col_name}",
            labels={'x': col_name, 'y': 'Count'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        # Show only top 10 categories for pie chart
        top_categories = value_counts.head(10)
        
        fig_pie = px.pie(
            values=top_categories.values,
            names=top_categories.index,
            title=f"Pie Chart of {col_name} (Top 10)"
        )
        st.plotly_chart(fig_pie, use_container_width=True)


def show_bivariate_analysis(dataset: Dataset):
    """Show bivariate analysis."""
    
    st.subheader("🔗 Bivariate Analysis")
    
    numeric_cols = dataset.data.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.info("Need at least 2 numeric variables for bivariate analysis.")
        return
    
    tab1, tab2 = st.tabs(["Correlation Analysis", "Scatter Plots"])
    
    with tab1:
        st.write("**Correlation Matrix:**")
        
        # Calculate correlation matrix
        corr_matrix = dataset.data[numeric_cols].corr()
        
        # Create heatmap
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title="Correlation Heatmap",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Strong correlations
        st.write("**Strong Correlations (|r| > 0.7):**")
        
        strong_corrs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    strong_corrs.append({
                        'Variable 1': corr_matrix.columns[i],
                        'Variable 2': corr_matrix.columns[j],
                        'Correlation': corr_val
                    })
        
        if strong_corrs:
            strong_corr_df = pd.DataFrame(strong_corrs)
            st.dataframe(strong_corr_df.round(4), use_container_width=True)
        else:
            st.info("No strong correlations found.")
    
    with tab2:
        st.write("**Scatter Plot Analysis:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            x_var = st.selectbox("Select X variable:", numeric_cols, key="scatter_x")
        
        with col2:
            y_var = st.selectbox("Select Y variable:", numeric_cols, key="scatter_y")
        
        if x_var and y_var and x_var != y_var:
            # Create scatter plot
            fig_scatter = px.scatter(
                dataset.data,
                x=x_var,
                y=y_var,
                title=f"Scatter Plot: {x_var} vs {y_var}",
                trendline="ols"
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Calculate correlation
            correlation = dataset.data[x_var].corr(dataset.data[y_var])
            st.metric("Correlation Coefficient", f"{correlation:.4f}")
            
            # Interpretation
            if abs(correlation) > 0.8:
                strength = "Very Strong"
            elif abs(correlation) > 0.6:
                strength = "Strong"
            elif abs(correlation) > 0.4:
                strength = "Moderate"
            elif abs(correlation) > 0.2:
                strength = "Weak"
            else:
                strength = "Very Weak"
            
            direction = "Positive" if correlation > 0 else "Negative"
            st.info(f"**Interpretation:** {strength} {direction} correlation")