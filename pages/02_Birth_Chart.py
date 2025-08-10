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
    
    # Debug toggle
    with st.expander("🔧 Debug Information", expanded=False):
        debug_mode = st.checkbox("Enable debug mode", key="debug_mode")
        if debug_mode:
            st.info("Debug mode will show detailed planetary analysis information.")
    
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
    processed_planets = set()
    
    # Debug: Check what planets we received
    if st.session_state.get('debug_mode', False):
        st.write("**Debug - Received planets:**", list(positions.keys()))
    
    # Simple analysis based on planetary positions and degrees
    for planet, data in positions.items():
        if planet in processed_planets:  # Avoid duplicates
            continue
        processed_planets.add(planet)
        
        degree = data.get('degree', 0)
        sign = data.get('sign', 0)
        
        # Handle different data structure formats
        if 'degree_in_sign' in data:
            degree = data['degree_in_sign']
        if 'sign_index' in data:
            sign = data['sign_index']
        
        # Debug information
        if st.session_state.get('debug_mode', False):
            st.write(f"**{planet}**: Sign {sign}, Degree {degree:.2f}")
        
        
        # Handle shadow planets separately
        if planet in ['Rahu', 'Ketu']:
            # Shadow planets strength based on degree and beneficial/malefic houses
            # Consider Rahu/Ketu strong in specific signs and degree ranges
            if planet == 'Rahu':
                # Rahu is considered strong in Gemini (2), Virgo (5), Aquarius (10)
                if sign in [2, 5, 10] and 0 <= degree <= 30:
                    strong_planets.append(planet)
                else:
                    weak_planets.append(planet)
            elif planet == 'Ketu':
                # Ketu is considered strong in Sagittarius (8), Pisces (11)
                if sign in [8, 11] and 0 <= degree <= 30:
                    strong_planets.append(planet)
                else:
                    weak_planets.append(planet)
            continue
        
        # Simple strength analysis based on degree and sign position
        # Strong if in early/middle degrees (5-25) of favorable signs
        is_strong = False
        
        if 5 <= degree <= 25:
            # Additional checks for exaltation/own sign (simplified)
            if planet == 'Sun' and sign in [0, 4]:  # Aries, Leo
                is_strong = True
            elif planet == 'Moon' and sign in [1, 3]:  # Taurus, Cancer
                is_strong = True
            elif planet == 'Mars' and sign in [0, 7]:  # Aries, Scorpio
                is_strong = True
            elif planet == 'Mercury' and sign in [2, 5]:  # Gemini, Virgo
                is_strong = True
            elif planet == 'Jupiter' and sign in [3, 8, 11]:  # Cancer, Sagittarius, Pisces
                is_strong = True
            elif planet == 'Venus' and sign in [1, 6]:  # Taurus, Libra
                is_strong = True
            elif planet == 'Saturn' and sign in [6, 9, 10]:  # Libra, Capricorn, Aquarius
                is_strong = True
            else:
                # Check if in good degree range but not in own sign
                if 10 <= degree <= 20:
                    is_strong = True
        else:
            # Even if not in ideal degree range, check for exaltation/own signs
            # with relaxed degree requirements
            if planet == 'Sun' and sign in [0, 4]:  # Aries (exaltation), Leo (own)
                is_strong = True
            elif planet == 'Moon' and sign in [1, 3]:  # Taurus (exaltation), Cancer (own)
                is_strong = True
            elif planet == 'Mars' and sign in [0, 7, 9]:  # Aries (own), Scorpio (own), Capricorn (exaltation)
                is_strong = True
            elif planet == 'Mercury' and sign in [2, 5]:  # Gemini (own), Virgo (own/exaltation)
                is_strong = True
            elif planet == 'Jupiter' and sign in [3, 8, 11]:  # Cancer (exaltation), Sagittarius (own), Pisces (own)
                is_strong = True
            elif planet == 'Venus' and sign in [1, 6, 11]:  # Taurus (own), Libra (own), Pisces (exaltation)
                is_strong = True
            elif planet == 'Saturn' and sign in [6, 9, 10]:  # Libra (exaltation), Capricorn (own), Aquarius (own)
                is_strong = True
        
        if is_strong:
            strong_planets.append(planet)
        else:
            weak_planets.append(planet)
    
    # Determine chart owner (strongest planet or Sun as default)
    if strong_planets:
        chart_owner = strong_planets[0]  # Take first strong planet
    else:
        chart_owner = "Sun"  # Default to Sun if no clear strong planet
    
    # Ensure we have some weak planets if strong list is too long
    if len(strong_planets) > 4:
        # Move some to weak (avoid duplicates)
        planets_to_move = strong_planets[4:]
        for planet in planets_to_move:
            if planet not in weak_planets:
                weak_planets.append(planet)
        strong_planets = strong_planets[:4]
    
    # Only add fallback entries if lists are completely empty (shouldn't happen with real data)
    if not strong_planets and not weak_planets:
        strong_planets = ["Sun", "Moon"]
        weak_planets = ["Mars", "Saturn"]
    elif not strong_planets:
        # If no strong planets, at least show the chart owner
        strong_planets = [chart_owner]
    elif not weak_planets:
        # If no weak planets, show some common ones that aren't in strong list
        all_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        weak_planets = [p for p in all_planets if p not in strong_planets][:2]
    
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
    # Use full width with padding for better layout
    st.markdown("""
    <style>
    /* Add padding to chart generation section */
    .chart-generation-container {
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        background-color: rgba(248, 249, 251, 0.5);
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Chart calculation options with padding
    with st.container():
        st.markdown('<div class="chart-generation-container">', unsafe_allow_html=True)
        
        st.subheader("📊 Chart Generation")
        
        chart_type = st.selectbox(
            "Select Chart Type",
            ["Generate Vedic Horoscope", "Traditional", "Divisional Charts"],
            help="Choose your preferred calculation method"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
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
