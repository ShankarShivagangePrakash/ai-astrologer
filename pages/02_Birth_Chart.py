import streamlit as st
from src.utils.page_utils import (
    create_standard_page_layout,
    create_birth_info_display,
    render_coming_soon_section,
    CHART_FEATURES
)
from components.VedicHoroscopeGenerator import create_kundali_widget
from src.astrology.prediction_engine import generate_detailed_prediction

def render_chart_summary(positions, birth_data):
    """Generate and display chart summary with strong/weak planets and chart owner"""
    st.subheader("📋 Chart Summary")
    
    # Analyze planetary strengths
    strong_planets, weak_planets, chart_owner = analyze_planetary_strengths(positions, birth_data)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**💪 Strong Planets:**")
        for planet in strong_planets:
            st.write(f"• {planet}")
    
    with col2:
        st.write("**⚠️ Weak Planets:**")
        for planet in weak_planets:
            st.write(f"• {planet}")
    
    with col3:
        st.write("**👑 Chart Owner:**")
        st.write(f"**{chart_owner}**")
        st.caption("Primary ruling planet")

def analyze_planetary_strengths(positions, birth_data):
    """Analyze planetary strengths and determine chart owner"""
    strong_planets = []
    weak_planets = []
    
    # Simple analysis based on planetary positions and degrees
    for planet, data in positions.items():
        if planet in ['Rahu', 'Ketu']:  # Skip shadow planets for strength analysis
            continue
            
        degree = data.get('degree', 0)
        sign = data.get('sign', 0)
        
        # Simple strength analysis based on degree and sign position
        # Strong if in early/middle degrees (5-25) of favorable signs
        if 5 <= degree <= 25:
            # Additional checks for exaltation/own sign (simplified)
            if planet == 'Sun' and sign in [0, 4]:  # Aries, Leo
                strong_planets.append(planet)
            elif planet == 'Moon' and sign in [1, 3]:  # Taurus, Cancer
                strong_planets.append(planet)
            elif planet == 'Mars' and sign in [0, 7]:  # Aries, Scorpio
                strong_planets.append(planet)
            elif planet == 'Mercury' and sign in [2, 5]:  # Gemini, Virgo
                strong_planets.append(planet)
            elif planet == 'Jupiter' and sign in [3, 8, 11]:  # Cancer, Sagittarius, Pisces
                strong_planets.append(planet)
            elif planet == 'Venus' and sign in [1, 6]:  # Taurus, Libra
                strong_planets.append(planet)
            elif planet == 'Saturn' and sign in [6, 9, 10]:  # Libra, Capricorn, Aquarius
                strong_planets.append(planet)
            else:
                # Check if in good degree range but not in own sign
                if 10 <= degree <= 20:
                    strong_planets.append(planet)
                else:
                    weak_planets.append(planet)
        else:
            weak_planets.append(planet)
    
    # Determine chart owner (strongest planet or Sun as default)
    if strong_planets:
        chart_owner = strong_planets[0]  # Take first strong planet
    else:
        chart_owner = "Sun"  # Default to Sun if no clear strong planet
    
    # Ensure we have some weak planets if strong list is too long
    if len(strong_planets) > 4:
        # Move some to weak
        weak_planets.extend(strong_planets[4:])
        strong_planets = strong_planets[:4]
    
    # Ensure we have some entries
    if not strong_planets:
        strong_planets = ["Sun", "Moon"]
    if not weak_planets:
        weak_planets = ["Mars", "Saturn"]
    
    return strong_planets, weak_planets, chart_owner

def render_detailed_chart_analysis(birth_data):
    """Generate and display detailed chart analysis"""
    st.subheader("🔬 Detailed Chart Analysis")
    
    with st.spinner("🔮 Generating comprehensive chart analysis..."):
        try:
            detailed_analysis = generate_detailed_prediction(birth_data)
            if detailed_analysis:
                st.markdown(detailed_analysis)
            else:
                st.warning("Unable to generate detailed analysis at this time. Please try again later.")
        except Exception as e:
            st.error(f"Error generating analysis: {str(e)}")
            st.info("💡 Basic chart has been generated successfully. Detailed analysis requires additional processing.")

def render_birth_chart_content(birth_data):
    """Render birth chart specific content"""
    # Center the chart generation content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Chart calculation options
        st.subheader("📊 Chart Generation")
        
        chart_type = st.selectbox(
            "Select Chart Type",
            ["Generate Vedic Horoscope", "Traditional", "Divisional Charts"],
            help="Choose your preferred calculation method"
        )
        
        if chart_type == "Generate Vedic Horoscope":
            positions = create_kundali_widget(birth_data)
            
            if positions:
                # Generate chart summary automatically
                st.markdown("---")
                render_chart_summary(positions, birth_data)
                
                # Generate detailed analysis automatically
                st.markdown("---")
                render_detailed_chart_analysis(birth_data)
                
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
