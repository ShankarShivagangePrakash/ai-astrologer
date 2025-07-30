import streamlit as st
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'components'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

# Import components and utilities
from config.settings import APP_CONFIG, load_custom_css, validate_environment
from src.utils.validators import initialize_session_state
from src.utils.ui_components import (
    render_sidebar_navigation, 
    render_header, 
    render_how_it_works,
    render_session_status,
    render_features_overview,
    render_footer
)
from components.birth_form import render_birth_form
from components.birth_data_display import render_birth_data_display

# Page configuration
st.set_page_config(
    page_title=APP_CONFIG["title"],
    page_icon=APP_CONFIG["icon"],
    layout=APP_CONFIG["layout"],
    initial_sidebar_state=APP_CONFIG["sidebar_state"]
)

def main():
    """Main application function"""
    # Initialize app
    load_custom_css()
    initialize_session_state()
    validate_environment()
    
    # Render UI components
    render_sidebar_navigation()
    render_header()
    
    # Show saved birth data if available
    if render_birth_data_display():
        st.markdown("---")
    
    render_how_it_works()
    render_birth_form()
    render_session_status()
    render_features_overview()
    render_footer()

if __name__ == "__main__":
    main()
