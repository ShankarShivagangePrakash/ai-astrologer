import streamlit as st
from src.utils.page_utils import (
    create_standard_page_layout,
    create_birth_info_display,
    render_coming_soon_section,
    CHART_FEATURES
)

def render_birth_chart_content(birth_data):
    """Render birth chart specific content"""
    col1, col2 = st.columns(2)
    
    with col1:
        create_birth_info_display(birth_data)
    
    with col2:
        render_coming_soon_section(
            "📊 Chart Generation", 
            CHART_FEATURES
        )

def main():
    page_config = {
        'title': '📊 Birth Chart Analysis',
        'icon': '📊',
        'subtitle': 'Detailed Natal Chart Calculation and Display',
        'content_callback': render_birth_chart_content,
        'page_id': 'birth_chart'
    }
    
    create_standard_page_layout(page_config)

if __name__ == "__main__":
    main()
