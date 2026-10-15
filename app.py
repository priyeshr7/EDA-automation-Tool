"""
EDA Automation Tool - Main Application Entry Point
A Streamlit web application for automated exploratory data analysis.
"""

import streamlit as st
from pages import preprocessing, analysis, requirements
from core.session_manager import SessionStateManager

# Configure Streamlit page
st.set_page_config(
    page_title="EDA Automation Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main(): 
    """Main application function with navigation."""
    
    # Initialize session state
    SessionStateManager.initialize_state()
    
    # Sidebar navigation
    st.sidebar.title("📊 EDA Automation Tool")
    st.sidebar.markdown("---")
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["🔧 Preprocessing", "📈 Analysis", "📋 Requirements"],
        key="navigation"
    )
    
    # Display data status in sidebar
    if SessionStateManager.is_data_loaded():
        st.sidebar.success("✅ Data loaded")
        dataset = SessionStateManager.get_data("dataset")
        if dataset:
            st.sidebar.info(f"Dataset: {dataset.name}")
            st.sidebar.info(f"Shape: {dataset.data.shape}")
    else:
        st.sidebar.warning("⚠️ No data loaded")
    
    st.sidebar.markdown("---")
    
    # Route to appropriate page
    if page == "🔧 Preprocessing":
        preprocessing.show()
    elif page == "📈 Analysis":
        analysis.show()
    elif page == "📋 Requirements":
        requirements.show()

if __name__ == "__main__":
    main()