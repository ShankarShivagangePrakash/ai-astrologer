import streamlit as st
from src.utils.page_utils import (
    create_standard_page_layout,
    render_standard_disclaimer,
    REMEDY_CATEGORIES
)
from src.utils.common import generate_ai_response

def generate_personalized_mantras(birth_data):
    """Generate AI-powered personalized mantra recommendations"""
    if not birth_data or not birth_data.get('date'):
        return None
    
    # Extract comprehensive location information
    location_info = birth_data.get('location', {})
    if isinstance(location_info, dict):
        city = location_info.get('city', '')
        state = location_info.get('state', '')
        country = location_info.get('country', '')
        latitude = location_info.get('latitude')
        longitude = location_info.get('longitude')
        coordinates = location_info.get('coordinates', {})
        if not latitude and coordinates:
            latitude = coordinates.get('latitude')
            longitude = coordinates.get('longitude')
        
        location_str = f"{city}, {state}, {country}" if state else f"{city}, {country}"
        if latitude and longitude:
            location_str += f" (Lat: {latitude:.4f}°, Long: {longitude:.4f}°)"
    else:
        location_str = birth_data.get('place', 'Not specified')
    
    timezone_offset = birth_data.get('timezone_offset', 0)
    
    prompt = f"""
    As a Vedic astrology expert, provide personalized mantra recommendations for someone born on:
    
    Date: {birth_data['date']}
    Time: {birth_data.get('time', 'Not specified')}
    Place: {location_str}
    Timezone Offset: {timezone_offset:+.1f} hours from UTC
    
    Based on the precise birth location coordinates and timezone, please provide:
    1. **Primary Mantra**: One main mantra based on their likely birth planetary influences considering geographical location
    2. **Daily Mantras**: 3-4 mantras for daily recitation suited to their birth time and location
    3. **Specific Purpose Mantras**: Mantras for career, health, relationships, and wealth
    4. **Recitation Guidelines**: Best times and methods for chanting considering their timezone
    5. **Location-specific Guidance**: Any regional considerations for mantra practice
    
    Format as clear sections with Sanskrit mantras and their English meanings.
    Focus on traditional Vedic mantras and their specific benefits based on precise birth coordinates.
    """
    
    return generate_ai_response(prompt)

def generate_personalized_gemstones(birth_data):
    """Generate AI-powered personalized gemstone recommendations"""
    if not birth_data or not birth_data.get('date'):
        return None
    
    # Extract comprehensive location information
    location_info = birth_data.get('location', {})
    if isinstance(location_info, dict):
        city = location_info.get('city', '')
        state = location_info.get('state', '')
        country = location_info.get('country', '')
        latitude = location_info.get('latitude')
        longitude = location_info.get('longitude')
        coordinates = location_info.get('coordinates', {})
        if not latitude and coordinates:
            latitude = coordinates.get('latitude')
            longitude = coordinates.get('longitude')
        
        location_str = f"{city}, {state}, {country}" if state else f"{city}, {country}"
        if latitude and longitude:
            location_str += f" (Lat: {latitude:.4f}°, Long: {longitude:.4f}°)"
    else:
        location_str = birth_data.get('place', 'Not specified')
    
    timezone_offset = birth_data.get('timezone_offset', 0)
    
    prompt = f"""
    As a Vedic gemstone expert, provide personalized gemstone recommendations for someone born on:
    
    Date: {birth_data['date']}
    Time: {birth_data.get('time', 'Not specified')}
    Place: {location_str}
    Timezone Offset: {timezone_offset:+.1f} hours from UTC
    
    Based on the precise birth location coordinates and timezone, please provide:
    1. **Primary Gemstone**: Main gemstone recommendation based on likely birth chart considering geographical location
    2. **Alternative Gemstones**: 2-3 alternative options suited to their birth coordinates
    3. **Metal Recommendations**: Best metals for setting (gold, silver, copper, etc.) based on planetary influences
    4. **Wearing Guidelines**: Which finger, day to start wearing, and precautions considering their timezone
    5. **Benefits**: Specific benefits each gemstone will provide based on birth location
    6. **Important Warnings**: What to avoid and consultation requirements
    7. **Regional Considerations**: Any location-specific factors for gemstone selection
    
    Focus on traditional Vedic gemstone science and safety guidelines.
    Always recommend professional consultation before wearing precious gemstones.
    Consider the geographical and cultural context of their birth location.
    """
    
    return generate_ai_response(prompt)

def generate_personalized_rituals(birth_data):
    """Generate AI-powered personalized ritual recommendations"""
    if not birth_data or not birth_data.get('date'):
        return None
    
    # Extract comprehensive location information
    location_info = birth_data.get('location', {})
    if isinstance(location_info, dict):
        city = location_info.get('city', '')
        state = location_info.get('state', '')
        country = location_info.get('country', '')
        latitude = location_info.get('latitude')
        longitude = location_info.get('longitude')
        coordinates = location_info.get('coordinates', {})
        if not latitude and coordinates:
            latitude = coordinates.get('latitude')
            longitude = coordinates.get('longitude')
        
        location_str = f"{city}, {state}, {country}" if state else f"{city}, {country}"
        if latitude and longitude:
            location_str += f" (Lat: {latitude:.4f}°, Long: {longitude:.4f}°)"
    else:
        location_str = birth_data.get('place', 'Not specified')
    
    timezone_offset = birth_data.get('timezone_offset', 0)
    
    prompt = f"""
    As a Vedic ritual expert, provide personalized ritual recommendations for someone born on:
    
    Date: {birth_data['date']}
    Time: {birth_data.get('time', 'Not specified')}
    Place: {location_str}
    Timezone Offset: {timezone_offset:+.1f} hours from UTC
    
    Based on the precise birth location coordinates and timezone, please provide:
    1. **Daily Rituals**: Morning and evening practices suited to their birth influences and local sunrise/sunset times
    2. **Weekly Rituals**: Specific day-based practices considering their geographical location
    3. **Seasonal Rituals**: Practices for different times of the year based on their hemisphere and climate
    4. **Remedial Rituals**: Specific rituals to strengthen weak planetary influences based on birth coordinates
    5. **Festival Observances**: Important festivals to observe for their birth pattern, including regional festivals
    6. **Practical Guidelines**: Step-by-step instructions for key rituals adapted to their location and timezone
    7. **Direction and Timing**: Proper directions for worship and auspicious times based on their coordinates
    
    Focus on practical, achievable rituals that can be performed at home.
    Include both simple daily practices and more elaborate remedial ceremonies.
    Consider local customs and seasonal variations based on their geographical location.
    """
    
    return generate_ai_response(prompt)

def generate_personalized_donations(birth_data):
    """Generate AI-powered personalized donation recommendations"""
    if not birth_data or not birth_data.get('date'):
        return None
    
    # Extract comprehensive location information
    location_info = birth_data.get('location', {})
    if isinstance(location_info, dict):
        city = location_info.get('city', '')
        state = location_info.get('state', '')
        country = location_info.get('country', '')
        latitude = location_info.get('latitude')
        longitude = location_info.get('longitude')
        coordinates = location_info.get('coordinates', {})
        if not latitude and coordinates:
            latitude = coordinates.get('latitude')
            longitude = coordinates.get('longitude')
        
        location_str = f"{city}, {state}, {country}" if state else f"{city}, {country}"
        if latitude and longitude:
            location_str += f" (Lat: {latitude:.4f}°, Long: {longitude:.4f}°)"
    else:
        location_str = birth_data.get('place', 'Not specified')
    
    timezone_offset = birth_data.get('timezone_offset', 0)
    
    prompt = f"""
    As a Vedic charity expert, provide personalized donation recommendations for someone born on:
    
    Date: {birth_data['date']}
    Time: {birth_data.get('time', 'Not specified')}
    Place: {location_str}
    Timezone Offset: {timezone_offset:+.1f} hours from UTC
    
    Based on the precise birth location coordinates and timezone, please provide:
    1. **Planetary Donations**: Specific items to donate based on likely planetary influences considering their birth location
    2. **Day-wise Donations**: What to donate on different days of the week, adapted to their timezone
    3. **Beneficial Recipients**: Who to give donations to for maximum spiritual benefit, including local organizations
    4. **Amounts and Timing**: Auspicious amounts and best times for donations considering their geographical location
    5. **Special Occasions**: Important dates for charitable giving based on regional calendar and festivals
    6. **Alternative Service**: Non-monetary ways to serve and gain spiritual merit suited to their location
    7. **Local Community**: Region-specific charitable opportunities and cultural considerations
    
    Focus on traditional Vedic principles of dana (charity) and their spiritual significance.
    Include both material donations and acts of service.
    Consider local customs, economic conditions, and cultural context based on their geographical location.
    """
    
    return generate_ai_response(prompt)

def render_remedies_content(birth_data):
    """Render AI-powered remedies specific content"""
    if not birth_data or not birth_data.get('date'):
        st.warning("⚠️ Please enter your birth date in the Birth Chart section to get personalized remedial recommendations.")
        st.info("""
        **What are Vedic Remedies?**
        
        Vedic remedies are time-tested spiritual practices designed to:
        
        **🔮 Mantras** - Sacred sounds that harmonize planetary energies
        **💎 Gemstones** - Natural crystals that strengthen beneficial planetary influences  
        **🕉️ Rituals** - Spiritual practices to balance karmic energies
        **🙏 Donations** - Charitable acts that generate positive karma
        
        Personalized recommendations will be provided based on your birth chart analysis.
        """)
        
        # Show general remedies when no birth data
        render_general_remedies()
        return
    
    st.success("✨ Generating personalized remedial recommendations based on your birth chart...")
    
    # Remedy categories with AI-powered content
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔮 Mantras",
        "💎 Gemstones", 
        "🕉️ Rituals",
        "🙏 Donations"
    ])
    
    with tab1:
        st.subheader("🔮 Mantra Recommendations")
        with st.spinner("🔮 Analyzing your planetary influences for mantra suggestions..."):
            mantra_recommendations = generate_personalized_mantras(birth_data)
        
        if mantra_recommendations:
            st.markdown(mantra_recommendations)
        else:
            st.error("❌ Unable to generate mantra recommendations. Please try again.")
        
        st.info("💡 **Important**: Mantras are most effective when chanted with devotion and consistency. Start with shorter sessions and gradually increase duration.")
    
    with tab2:
        st.subheader("💎 Gemstone Analysis")
        with st.spinner("💎 Calculating your gemstone compatibility..."):
            gemstone_recommendations = generate_personalized_gemstones(birth_data)
        
        if gemstone_recommendations:
            st.markdown(gemstone_recommendations)
        else:
            st.error("❌ Unable to generate gemstone recommendations. Please try again.")
        
        st.warning("⚠️ **Critical**: Always consult a qualified gemologist and astrologer before wearing any precious gemstone. Incorrect gemstones can have adverse effects.")
    
    with tab3:
        st.subheader("🕉️ Ritual Practices")
        with st.spinner("🕉️ Designing your spiritual practice routine..."):
            ritual_recommendations = generate_personalized_rituals(birth_data)
        
        if ritual_recommendations:
            st.markdown(ritual_recommendations)
        else:
            st.error("❌ Unable to generate ritual recommendations. Please try again.")
        
        st.info("🕯️ **Guidance**: Start with simple daily practices. Consistency is more important than complexity in spiritual practices.")
    
    with tab4:
        st.subheader("🙏 Charity & Service")
        with st.spinner("🙏 Identifying your most beneficial charitable acts..."):
            donation_recommendations = generate_personalized_donations(birth_data)
        
        if donation_recommendations:
            st.markdown(donation_recommendations)
        else:
            st.error("❌ Unable to generate donation recommendations. Please try again.")
        
        st.success("✨ **Remember**: The intention behind charity is more important than the amount. Give with a pure heart and genuine desire to help others.")
    
    render_standard_disclaimer()

def render_general_remedies():
    """Render general remedies when no birth data is available"""
    st.subheader("🌟 General Vedic Remedies")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔮 Universal Mantras",
        "💎 Gemstone Basics", 
        "🕉️ Daily Practices",
        "🙏 General Charity"
    ])
    
    with tab1:
        st.write("**🔮 Universal Mantras for All:**")
        st.write("""
        - **Om Gam Ganapataye Namaha** - Removes obstacles
        - **Om Namah Shivaya** - Overall spiritual protection
        - **Gayatri Mantra** - Universal enlightenment
        - **Mahamrityunjaya Mantra** - Health and longevity
        - **Om Shri Ganeshaya Namaha** - Success in endeavors
        """)
    
    with tab2:
        st.write("**💎 Gemstone Guidelines:**")
        st.write("""
        - Always consult an expert before wearing gemstones
        - Natural, untreated stones are most effective
        - Proper purification and energization is essential
        - Wear on the correct finger and day
        - Remove during illness or negative periods
        """)
    
    with tab3:
        st.write("**🕉️ Daily Spiritual Practices:**")
        st.write("""
        - Morning prayers and meditation
        - Evening gratitude practice
        - Regular temple visits
        - Reading sacred texts
        - Yoga and pranayama
        """)
    
    with tab4:
        st.write("**🙏 Universal Charitable Acts:**")
        st.write("""
        - Feed the hungry and poor
        - Help elderly and disabled
        - Support education for underprivileged
        - Plant trees and protect environment
        - Donate to temples and spiritual causes
        """)

def main():
    page_config = {
        'title': '💎 Vedic Remedies',
        'icon': '💎',
        'subtitle': 'Personalized Remedial Measures for Better Life',
        'content_callback': render_remedies_content,
        'page_id': 'remedies'
    }
    
    create_standard_page_layout(page_config)

if __name__ == "__main__":
    main()
