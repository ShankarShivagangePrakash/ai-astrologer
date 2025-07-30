import streamlit as st
from src.utils.page_utils import (
    create_standard_page_layout,
    render_coming_soon_section,
    DASHA_FEATURES
)

def render_dasha_content(birth_data):
    """Render dasha analysis specific content"""
    col1, col2 = st.columns(2)
    
    with col1:
        render_coming_soon_section(
            "🕐 Current Dasha Information", 
            [
                "Current Mahadasha period and effects",
                "Current Antardasha period analysis", 
                "Remaining time in current periods",
                "Predictions for ongoing phases"
            ]
        )
    
    with col2:
        render_coming_soon_section(
            "🕐 Dasha Timeline",
            [
                "Complete Vimshottari Dasha timeline",
                "Past, present, and future periods",
                "Major life events timing", 
                "Favorable and challenging periods"
            ]
        )
    
    st.markdown("---")
    st.subheader("🔍 About Dasha System")
    st.write("""
    **What is Dasha?**
    
    Dasha is a unique planetary period system in Vedic Astrology that divides a person's life 
    into different periods ruled by different planets. The most commonly used system is 
    **Vimshottari Dasha**, which spans 120 years.
    
    **Key Features:**
    - Each planet gets a specific period to influence your life
    - The sequence and duration are fixed based on ancient calculations
    - Provides timing for major life events and changes
    - Helps in understanding life phases and their characteristics
    """)

def main():
    page_config = {
        'title': '💫 Dasha Period Analysis',
        'icon': '💫',
        'subtitle': 'Planetary Period Predictions and Timeline',
        'content_callback': render_dasha_content,
        'page_id': 'dasha'
    }
    
    create_standard_page_layout(page_config)

if __name__ == "__main__":
    main()
