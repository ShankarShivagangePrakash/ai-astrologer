import streamlit as st
from src.utils.page_utils import (
    create_standard_page_layout,
    render_coming_soon_section,
    DASHA_FEATURES
)

import streamlit as st
from src.utils.page_utils import (
    create_standard_page_layout,
    render_coming_soon_section,
    DASHA_FEATURES
)
from src.calculations.dasha_calculator import VimshottariDashaCalculator
from datetime import datetime, timedelta

def render_current_dasha_info(dasha_data):
    """Render current dasha information"""
    if not dasha_data:
        st.error("❌ Unable to calculate dasha information")
        return
    
    st.subheader(f"🔮 Current Mahadasha: {dasha_data['current_planet']}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Current Period", 
            f"{dasha_data['current_planet']}", 
            f"{dasha_data['total_period_years']} years total"
        )
    
    with col2:
        st.metric(
            "Elapsed Time", 
            f"{dasha_data['elapsed_years']:.1f} years",
            f"{(dasha_data['elapsed_years']/dasha_data['total_period_years']*100):.1f}% complete"
        )
    
    with col3:
        st.metric(
            "Remaining Time", 
            f"{dasha_data['remaining_years']:.1f} years",
            f"Until {dasha_data['end_date'].strftime('%b %Y')}"
        )
    
    # Progress bar
    progress = dasha_data['elapsed_years'] / dasha_data['total_period_years']
    st.progress(progress)
    st.caption(f"Dasha started: {dasha_data['dasha_start_date'].strftime('%d %b %Y')} | "
               f"Ends: {dasha_data['end_date'].strftime('%d %b %Y')}")

def render_dasha_timeline(timeline_data):
    """Render complete dasha timeline from birth to 100 years"""
    if not timeline_data:
        st.error("❌ Unable to generate timeline")
        return
    
    st.subheader("📅 Complete Life Dasha Timeline (Birth to 100 Years)")
    
    try:
        # Prepare data for comprehensive table
        table_data = []
        current_date = datetime.now()
        
        # Process all periods in timeline
        for period in timeline_data:
            # Determine status
            if period.get('is_current', False):
                status = "🔴 Current"
                duration = f"{period['elapsed_years']:.1f} / {period['period_years']} years"
                progress = f"{(period['elapsed_years']/period['period_years']*100):.1f}%"
                time_info = f"{period['remaining_years']:.1f} years remaining"
            elif period.get('is_past', False):
                status = "⚪ Past"
                duration = f"{period['period_years']} years"
                progress = "Completed"
                days_ago = (current_date - period['end_date']).days
                if days_ago > 0:
                    time_info = f"Ended {days_ago} days ago"
                else:
                    time_info = "Recently ended"
            else:
                status = "🔵 Future"
                duration = f"{period['period_years']} years"
                progress = "Not started"
                days_until = (period['start_date'] - current_date).days
                if days_until > 0:
                    time_info = f"Starts in {days_until} days"
                else:
                    time_info = "Starting soon"
            
            table_data.append({
                "Status": status,
                "Planet": period['planet'],
                "Start Date": period['start_date'].strftime('%d %b %Y'),
                "End Date": period['end_date'].strftime('%d %b %Y'),
                "Duration": duration,
                "Progress": progress,
                "Time Info": time_info
            })
        
        # Display comprehensive table
        st.dataframe(table_data, use_container_width=True, hide_index=True)
        
        # Show summary statistics
        col1, col2, col3 = st.columns(3)
        
        past_count = sum(1 for p in timeline_data if p.get('is_past', False))
        current_count = sum(1 for p in timeline_data if p.get('is_current', False))
        future_count = len(timeline_data) - past_count - current_count
        
        with col1:
            st.metric("Past Periods", past_count, "⚪")
        with col2:
            st.metric("Current Period", current_count, "🔴")
        with col3:
            st.metric("Future Periods", future_count, "🔵")
        
        st.caption(f"📍 Complete Dasha timeline from birth to 100 years ({len(timeline_data)} total periods)")
        
    except Exception as e:
        st.error(f"Error generating comprehensive timeline: {str(e)}")
        # Simple fallback
        st.write("Basic timeline display:")
        for i, period in enumerate(timeline_data[:10]):
            st.write(f"{i+1}. {period['planet']} - {period['start_date'].strftime('%Y')} to {period['end_date'].strftime('%Y')}")

def render_dasha_content(birth_data):
    """Render dasha analysis specific content"""
    
    # Check if birth data is available
    if not birth_data or not birth_data.get('date') or not birth_data.get('time'):
        st.warning("⚠️ Birth date and time required for Dasha calculations")
        st.info("Please enter your birth information in the Home page to see your Dasha periods")
        
        # Show coming soon sections as fallback
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
        return
    
    # Calculate Dasha information
    try:
        calculator = VimshottariDashaCalculator()
        
        with st.spinner("🔮 Calculating your Dasha periods..."):
            # Get current dasha
            current_dasha = calculator.get_current_dasha(birth_data['date'], birth_data['time'])
            
            # Get complete life timeline from birth to 100 years
            timeline = calculator.get_complete_life_dasha_timeline(birth_data['date'], birth_data['time'])
        
        if current_dasha and timeline:
            # Render current dasha information
            render_current_dasha_info(current_dasha)
                        
            # Render timeline
            render_dasha_timeline(timeline)
            
            
        else:
            st.error("❌ Unable to calculate Dasha information. Please check your birth data.")
    
    except Exception as e:
        st.error(f"❌ Error calculating Dasha: {str(e)}")
        st.info("Please ensure your birth date and time are correct.")
    
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
