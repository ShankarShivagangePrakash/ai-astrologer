import streamlit as st
from src.utils.page_utils import (
    create_standard_page_layout,
    create_birth_info_display,
    render_coming_soon_section,
    CHART_FEATURES
)
from components.VedicHoroscopeGenerator import create_kundali_widget

def render_birth_chart_content(birth_data):
    """Render birth chart specific content"""
    col1, col2 = st.columns(2)
    
    with col1:
        create_birth_info_display(birth_data)
    
    with col2:
        # Chart calculation options
        st.subheader("📊 Chart Generation")
        
        chart_type = st.selectbox(
            "Select Chart Type",
            ["Generate Vedic Horoscope", "Traditional", "Divisional Charts"],
            help="Choose your preferred calculation method"
        )
        
        if chart_type == "Generate Vedic Horoscope":
            st.info("🔬 High-precision astronomical calculations")
            positions = create_kundali_widget(birth_data)
            
            if positions:
                with st.expander("📋 Detailed Planetary Positions"):
                    from components.VedicHoroscopeGenerator import VedicHoroscopeGenerator
                    calculator = VedicHoroscopeGenerator()
                    report_data = calculator.create_detailed_report(positions)
                    if report_data:
                        st.dataframe(report_data, use_container_width=True)
        else:
            render_coming_soon_section(
                f"📊 {chart_type}", 
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
