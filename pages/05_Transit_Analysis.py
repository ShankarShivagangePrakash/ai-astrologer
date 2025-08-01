import streamlit as st
from src.utils.page_utils import create_standard_page_layout
from src.calculations.planetary_afflictions import PlanetaryAfflictionsCalculator
from datetime import datetime, timedelta
import pandas as pd

def render_current_afflictions(current_afflictions):
    """Render currently active afflictions"""
    if not current_afflictions:
        st.success("✅ No major planetary afflictions are currently active!")
        return
    
    st.error(f"⚠️ {len(current_afflictions)} Active Affliction(s)")
    
    for affliction in current_afflictions:
        with st.expander(f"🔴 {affliction['name']} - {affliction.get('phase', 'Active')}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Current Age",
                    f"{affliction.get('start_age', 'N/A')} years",
                    f"Started"
                )
            
            with col2:
                if 'remaining_days' in affliction:
                    remaining_years = round(affliction['remaining_days'] / 365.25, 1)
                    st.metric(
                        "Remaining",
                        f"{remaining_years} years",
                        f"{affliction['remaining_days']} days"
                    )
            
            with col3:
                st.metric(
                    "Intensity",
                    affliction.get('intensity', 'Medium'),
                    f"Duration: {affliction.get('duration_years', 'N/A')} years"
                )
            
            # Effects and remedies
            st.write(f"**🎯 Effects:** {affliction.get('effects', 'General challenging period')}")
            st.write(f"**🔮 Remedies:** {affliction.get('remedies', 'Spiritual practices and charity')}")
            
            if affliction['name'] == 'Sade Sathi':
                st.info(f"**Phase:** {affliction.get('phase', 'Unknown')} - Moon Sign: {affliction.get('moon_sign', 'Unknown')}")

def render_upcoming_afflictions(upcoming_afflictions):
    """Render upcoming afflictions"""
    if not upcoming_afflictions:
        st.success("✅ No major afflictions expected in the next 5 years!")
        return
    
    st.warning(f"⏳ {len(upcoming_afflictions)} Upcoming Affliction(s) in Next 5 Years")
    
    for affliction in upcoming_afflictions:
        with st.expander(f"🟡 {affliction['name']} - Starts {affliction['start_date'].strftime('%B %Y')}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Starts At Age",
                    f"{affliction.get('start_age', 'N/A')} years",
                    f"{affliction['start_date'].strftime('%b %d, %Y')}"
                )
            
            with col2:
                if 'days_until_start' in affliction:
                    years_until = round(affliction['days_until_start'] / 365.25, 1)
                    st.metric(
                        "Time Until Start",
                        f"{years_until} years",
                        f"{affliction['days_until_start']} days"
                    )
            
            with col3:
                st.metric(
                    "Duration",
                    f"{affliction.get('duration_years', 'N/A')} years",
                    f"Ends at age {affliction.get('end_age', 'N/A')}"
                )
            
            st.write(f"**🎯 Expected Effects:** {affliction.get('effects', 'Challenging period ahead')}")
            st.write(f"**🔮 Recommended Remedies:** {affliction.get('remedies', 'Start spiritual practices early')}")

def render_lifetime_afflictions_timeline(timeline):
    """Render complete lifetime afflictions timeline"""
    if not timeline:
        st.error("❌ Unable to calculate afflictions timeline")
        return
    
    st.subheader("🎯 Complete Lifetime Afflictions Timeline (Birth to 100 Years)")
    
    # Summary statistics
    summary = timeline.get('summary', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Sade Sathi Periods",
            summary.get('total_sade_sathi_periods', 0),
            f"{summary.get('total_sade_sathi_years', 0)} years total"
        )
    
    with col2:
        st.metric(
            "Ashtama Shani Periods", 
            summary.get('total_ashtama_periods', 0),
            f"{summary.get('total_ashtama_years', 0)} years total"
        )
    
    with col3:
        kuja_status = "Present" if summary.get('lifetime_kuja_dosha', False) else "Absent"
        st.metric(
            "Kuja Dosha",
            kuja_status,
            "Lifetime effect"
        )
    
    with col4:
        kala_sarpa_status = "Present" if summary.get('lifetime_kala_sarpa', False) else "Absent"
        st.metric(
            "Kala Sarpa Dosha",
            kala_sarpa_status,
            "Lifetime effect"
        )
    
    # Year span summary table
    st.subheader("📅 Affliction Period Year Spans")
    
    # Create year span table
    year_spans = []
    
    # Add Sade Sathi year spans
    for i, period in enumerate(timeline.get('sade_sathi_periods', []), 1):
        start_date_str = period['start_date'].strftime('%b %Y')
        end_date_str = period['end_date'].strftime('%b %Y')
        
        year_spans.append({
            'Affliction Type': 'Sade Sathi',
            'Period #': f"Period {period.get('cycle_number', i)}",
            'Phase': period.get('phase', 'Unknown'),
            'Date Range': f"{start_date_str} to {end_date_str}",
            'Start Age': f"{period.get('start_age', 'N/A')} years",
            'End Age': f"{period.get('end_age', 'N/A')} years",
            'Duration': f"{period.get('duration_years', 'N/A')} years",
            'Intensity': period.get('intensity', 'Medium')
        })
    
    # Add Ashtama Shani year spans
    for i, period in enumerate(timeline.get('ashtama_shani_periods', []), 1):
        start_date_str = period['start_date'].strftime('%b %Y')
        end_date_str = period['end_date'].strftime('%b %Y')
        
        year_spans.append({
            'Affliction Type': 'Ashtama Shani',
            'Period #': f"Period {period.get('cycle_number', i)}",
            'Phase': 'Complete Period',
            'Date Range': f"{start_date_str} to {end_date_str}",
            'Start Age': f"{period.get('start_age', 'N/A')} years",
            'End Age': f"{period.get('end_age', 'N/A')} years",
            'Duration': f"{period.get('duration_years', 'N/A')} years",
            'Intensity': period.get('intensity', 'Very High')
        })
    
    # Sort by start age
    year_spans.sort(key=lambda x: float(x['Start Age'].replace(' years', '')) if x['Start Age'] != 'N/A years' else 0)
    
    if year_spans:
        df_spans = pd.DataFrame(year_spans)
        st.dataframe(df_spans, use_container_width=True, hide_index=True)
        
        # Add interpretation
        st.info(f"""
        **📊 Lifetime Saturn Afflictions Overview:**
        - **Sade Sathi**: {len(timeline.get('sade_sathi_periods', []))} periods × 7.5 years = {summary.get('total_sade_sathi_years', 0)} years total
        - **Ashtama Shani**: {len(timeline.get('ashtama_shani_periods', []))} periods × 2.5 years = {summary.get('total_ashtama_years', 0)} years total
        - **Total Saturn Affliction Years**: {summary.get('total_sade_sathi_years', 0) + summary.get('total_ashtama_years', 0)} years out of 100-year lifespan
        - **Life Impact**: Approximately {round((summary.get('total_sade_sathi_years', 0) + summary.get('total_ashtama_years', 0)) / 100 * 100, 1)}% of lifetime under major Saturn influences
        
        **Note:** Every person experiences exactly 4 Sade Sathi periods (every ~29.5 years) and multiple Ashtama Shani periods during their lifetime.
        """)
    else:
        st.info("ℹ️ No major Saturn affliction periods found in lifetime timeline")
    
    # Detailed timeline table
    st.subheader("🗓️ Detailed Timeline")
    
    # Combine all periods for timeline
    all_periods = []
    
    # Add Sade Sathi periods
    for period in timeline.get('sade_sathi_periods', []):
        all_periods.append({
            'Affliction': f"Sade Sathi ({period.get('phase', 'Unknown')})",
            'Start Date': period['start_date'].strftime('%b %Y'),
            'End Date': period['end_date'].strftime('%b %Y'),
            'Start Age': f"{period.get('start_age', 'N/A')} years",
            'End Age': f"{period.get('end_age', 'N/A')} years",
            'Duration': f"{period.get('duration_years', 'N/A')} years",
            'Intensity': period.get('intensity', 'Medium'),
            'Key Effects': period.get('effects', 'Challenging period')[:60] + "..."
        })
    
    # Add Ashtama Shani periods
    for period in timeline.get('ashtama_shani_periods', []):
        all_periods.append({
            'Affliction': 'Ashtama Shani',
            'Start Date': period['start_date'].strftime('%b %Y'),
            'End Date': period['end_date'].strftime('%b %Y'),
            'Start Age': f"{period.get('start_age', 'N/A')} years",
            'End Age': f"{period.get('end_age', 'N/A')} years",
            'Duration': f"{period.get('duration_years', 'N/A')} years",
            'Intensity': period.get('intensity', 'Very High'),
            'Key Effects': period.get('effects', 'Major transformations')[:60] + "..."
        })
    
    # Sort by start date
    all_periods.sort(key=lambda x: datetime.strptime(x['Start Date'], '%b %Y'))
    
    if all_periods:
        df = pd.DataFrame(all_periods)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No major planetary affliction periods found in lifetime")

def render_birth_chart_doshas(kuja_dosha, kala_sarpa_dosha):
    """Render birth chart doshas (Kuja Dosha and Kala Sarpa Dosha)"""
    st.subheader("🏠 Birth Chart Doshas (Lifetime Effects)")
    
    col1, col2 = st.columns(2)
    
    # Kuja Dosha
    with col1:
        if kuja_dosha and kuja_dosha.get('present', False):
            st.error("🔴 Kuja Dosha (Manglik) Present")
            st.write(f"**Mars House:** {kuja_dosha.get('mars_house', 'Unknown')}")
            st.write(f"**Mars Sign:** {kuja_dosha.get('mars_sign', 'Unknown')}")
            st.write(f"**Severity:** {kuja_dosha.get('severity', 'Medium')}")
            st.write(f"**Effects:** {kuja_dosha.get('effects', 'Marital challenges')}")
            st.write(f"**Marriage:** {kuja_dosha.get('marriage_compatibility', 'Consult astrologer')}")
            st.info(f"**Remedies:** {kuja_dosha.get('remedies', 'Hanuman worship, Tuesday fasting')}")
        else:
            st.success("✅ No Kuja Dosha")
            if kuja_dosha:
                st.write(f"**Mars House:** {kuja_dosha.get('mars_house', 'Unknown')}")
                st.write(f"**Mars Sign:** {kuja_dosha.get('mars_sign', 'Unknown')}")
                st.write("**Marriage:** Normal compatibility")
    
    # Kala Sarpa Dosha
    with col2:
        if kala_sarpa_dosha and kala_sarpa_dosha.get('present', False):
            st.error("🔴 Kala Sarpa Dosha Present")
            st.write(f"**Intensity:** {kala_sarpa_dosha.get('intensity', 'High')}")
            st.write(f"**Rahu Sign:** {kala_sarpa_dosha.get('rahu_sign', 'Unknown')}")
            st.write(f"**Ketu Sign:** {kala_sarpa_dosha.get('ketu_sign', 'Unknown')}")
            st.write(f"**Effects:** {kala_sarpa_dosha.get('effects', 'Obstacles and delays')}")
            st.success(f"**Positive:** {kala_sarpa_dosha.get('positive_aspects', 'Spiritual growth')}")
            st.info(f"**Remedies:** {kala_sarpa_dosha.get('remedies', 'Rahu-Ketu mantras')}")
        else:
            st.success("✅ No Kala Sarpa Dosha")
            st.write("**Effect:** Balanced planetary influences")

def render_transit_content(birth_data):
    """Render transit analysis with planetary afflictions"""
    if not birth_data or not birth_data.get('date'):
        st.warning("⚠️ Please enter your birth date in the Birth Chart section to see planetary afflictions analysis.")
        st.info("""
        **What are Planetary Afflictions?**
        
        Planetary afflictions are challenging periods in Vedic astrology caused by:
        
        **🪐 Sade Sathi** - Saturn's 7.5-year transit through 12th, 1st, and 2nd houses from Moon sign
        **🔥 Ashtama Shani** - Saturn's 2.5-year transit through 8th house from Moon sign  
        **⚔️ Kuja Dosha** - Mars in challenging houses causing marital discord
        **🐍 Kala Sarpa Dosha** - All planets trapped between Rahu-Ketu axis
        
        This analysis provides:
        - Current active afflictions and their effects
        - Complete lifetime timeline from birth to 100 years
        - Remedies and spiritual practices for each period
        - Intensity levels and preparation guidance
        """)
        return
    
    birth_date = birth_data['date']
    
    try:
        # Initialize calculator
        with st.spinner("🔮 Calculating planetary afflictions from birth to 100 years..."):
            calculator = PlanetaryAfflictionsCalculator()
            
            # Get complete timeline
            complete_timeline = calculator.get_complete_afflictions_timeline(birth_date)
            
            # Get current afflictions
            current_afflictions = calculator.get_current_afflictions(birth_date)
            
            # Get upcoming afflictions
            upcoming_afflictions = calculator.get_upcoming_afflictions(birth_date, years_ahead=5)
        
        # Display current afflictions
        st.subheader("🔴 Currently Active Afflictions")
        render_current_afflictions(current_afflictions)
        
        st.markdown("---")
        
        # Display upcoming afflictions
        st.subheader("🟡 Upcoming Afflictions (Next 5 Years)")
        render_upcoming_afflictions(upcoming_afflictions)
        
        st.markdown("---")
        
        # Display birth chart doshas
        kuja_dosha = complete_timeline.get('kuja_dosha')
        kala_sarpa_dosha = complete_timeline.get('kala_sarpa_dosha')
        render_birth_chart_doshas(kuja_dosha, kala_sarpa_dosha)
        
        st.markdown("---")
        
        # Display complete timeline
        render_lifetime_afflictions_timeline(complete_timeline)
        
        st.markdown("---")
        
        # Educational content
        st.subheader("📚 Understanding Planetary Afflictions")
        
        tab1, tab2, tab3, tab4 = st.tabs(["🪐 Sade Sathi", "🔥 Ashtama Shani", "⚔️ Kuja Dosha", "🐍 Kala Sarpa"])
        
        with tab1:
            st.write("""
            **Sade Sathi (Seven and Half Years of Saturn)**
            
            **🔍 What is it?**
            - Saturn's transit through 12th, 1st, and 2nd houses from your Moon sign
            - Occurs approximately every 29.5 years (Saturn's orbital period)
            - Duration: 7.5 years divided into three phases
            
            **📊 Three Phases:**
            1. **Rising (Arohini)** - 12th house: Initial challenges, preparation period
            2. **Peak (Madhya)** - 1st house: Maximum intensity, major life changes  
            3. **Setting (Avarohi)** - 2nd house: Gradual relief, lessons integration
            
            **🎯 Common Effects:**
            - Career changes and professional challenges
            - Health issues and medical expenses
            - Relationship stress and family conflicts
            - Financial constraints and increased responsibilities
            - Spiritual growth and maturity
            
            **🔮 Remedies:**
            - Saturday fasting and Saturn mantras
            - Donate black items (clothes, sesame, iron)
            - Help elderly people and disabled individuals
            - Wear blue sapphire (only after proper consultation)
            - Regular Hanuman Chalisa recitation
            """)
        
        with tab2:
            st.write("""
            **Ashtama Shani (Saturn in 8th House)**
            
            **🔍 What is it?**
            - Saturn's transit through the 8th house from your Moon sign
            - Duration: Approximately 2.5 years
            - Considered one of the most challenging Saturn transits
            
            **🎯 Key Effects:**
            - Major life transformations and sudden changes
            - Hidden enemies and unexpected obstacles
            - Health scares and chronic conditions
            - Accidents and injury possibilities
            - Inheritance and insurance matters
            - Deep psychological changes
            
            **🔮 Remedies:**
            - Regular Hanuman Chalisa and Bajrang Baan
            - Saturn mantras: "Om Sham Shanicharaya Namah"
            - Donate mustard oil on Saturdays
            - Help accident victims and disabled people
            - Wear iron ring on middle finger (Saturday)
            - Visit Shani temples and offer prayers
            """)
        
        with tab3:
            st.write("""
            **Kuja Dosha (Manglik Dosha)**
            
            **🔍 What is it?**
            - Mars positioned in 1st, 2nd, 4th, 7th, 8th, or 12th house
            - Affects approximately 50% of people
            - Primarily impacts marriage and relationships
            
            **🎯 Effects by House:**
            - **1st House:** Aggressive personality, leadership issues
            - **2nd House:** Family conflicts, speech problems
            - **4th House:** Property disputes, domestic issues
            - **7th House:** Direct impact on marriage and partnerships
            - **8th House:** Health issues, sudden changes
            - **12th House:** Hidden enemies, expenses
            
            **💒 Marriage Considerations:**
            - Manglik should ideally marry another Manglik
            - Age of marriage may be delayed
            - Remedies can reduce negative effects
            
            **🔮 Remedies:**
            - Tuesday fasting and Hanuman worship
            - Mars mantras: "Om Angarakaya Namah"
            - Wear red coral gemstone (after consultation)
            - Kumbh Vivah (ceremonial marriage to tree/idol)
            - Donate red items on Tuesdays
            """)
        
        with tab4:
            st.write("""
            **Kala Sarpa Dosha (Serpent Time Defect)**
            
            **🔍 What is it?**
            - All seven planets positioned between Rahu and Ketu
            - Creates a "serpent" formation in the birth chart
            - Affects life path and spiritual development
            
            **🎯 Key Effects:**
            - Obstacles and delays in achieving goals
            - Mental restlessness and anxiety
            - Repeated failures despite good efforts
            - Strong karmic lessons and spiritual tests
            - Unusual life experiences and unconventional path
            
            **✨ Positive Aspects:**
            - Enhanced intuition and psychic abilities
            - Strong spiritual inclinations
            - Ability to overcome major obstacles
            - Unique contributions to society
            - Deep understanding of life mysteries
            
            **🔮 Remedies:**
            - Visit Kalahasti temple (Andhra Pradesh)
            - Rahu-Ketu mantras and Navagraha prayers
            - Donate to serpent deities and conservation
            - Perform Sarpa Dosha Nivarana Puja
            - Regular meditation and spiritual practices
            - Help animals, especially snakes and reptiles
            """)
    
    except Exception as e:
        st.error(f"❌ Error calculating planetary afflictions: {str(e)}")
        st.info("Please try again or contact support if the problem persists.")

def main():
    page_config = {
        'title': '🌟 Transit Analysis',
        'icon': '🌟',
        'subtitle': 'Current Planetary Influences and Future Transits',
        'content_callback': render_transit_content,
        'page_id': 'transit'
    }
    
    create_standard_page_layout(page_config)

if __name__ == "__main__":
    main()
