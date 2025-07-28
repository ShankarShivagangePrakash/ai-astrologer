import streamlit as st
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Vedic Astrologer",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_custom_css():
    """Load custom CSS styling"""
    try:
        with open('assets/styles/custom.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # CSS file not found, continue without custom styling
        pass

def initialize_session_state():
    """Initialize session state variables"""
    if 'birth_data' not in st.session_state:
        st.session_state.birth_data = {}
    if 'chart_calculated' not in st.session_state:
        st.session_state.chart_calculated = False
    if 'predictions_generated' not in st.session_state:
        st.session_state.predictions_generated = False

def main():
    # Load custom styling
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar navigation
    st.sidebar.title("🌟 Navigation")
    st.sidebar.markdown("---")
    
    # Navigation buttons
    if st.sidebar.button("🏠 Home", use_container_width=True):
        st.rerun()
    if st.sidebar.button("📊 Birth Chart", use_container_width=True):
        st.switch_page("pages/02_📊_Birth_Chart.py")
    if st.sidebar.button("🔮 Predictions", use_container_width=True):
        st.switch_page("pages/03_🔮_Predictions.py")
    if st.sidebar.button("💫 Dasha Analysis", use_container_width=True):
        st.switch_page("pages/04_💫_Dasha_Analysis.py")
    if st.sidebar.button("🌟 Transit Analysis", use_container_width=True):
        st.switch_page("pages/05_🌟_Transit_Analysis.py")
    if st.sidebar.button("💎 Remedies", use_container_width=True):
        st.switch_page("pages/06_💎_Remedies.py")
    if st.sidebar.button("📋 Reports", use_container_width=True):
        st.switch_page("pages/07_📋_Reports.py")
    
    # Main content area
    st.title("🔮 Vedic Astrologer App")
    st.markdown("### Welcome to AI-Powered Vedic Astrology")
    st.write("Get personalized predictions based on ancient Hindu astrology combined with modern AI.")
    
    # Quick start section
    st.subheader("How It Works")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📅 **Step 1: Enter Birth Details**")
        st.write("Provide your birth date, time, and location for accurate calculations")
    
    with col2:
        st.success("🔮 **Step 2: Get AI Predictions**")
        st.write("Our AI analyzes your chart using traditional Vedic principles")
    
    with col3:
        st.warning("💎 **Step 3: Receive Remedies**")
        st.write("Get personalized suggestions for a better life")
    
    # Quick input section
    st.subheader("Quick Start")
    
    with st.expander("Enter Birth Details (Optional)", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            birth_date = st.date_input("Birth Date", value=datetime.now().date())
            birth_time = st.time_input("Birth Time", value=datetime.now().time())
        
        with col2:
            birth_place = st.text_input("Birth Place", placeholder="e.g., New Delhi, India")
            
        if st.button("Generate Quick Prediction", type="primary"):
            if birth_place:
                # Store in session state
                st.session_state.birth_data = {
                    'date': birth_date,
                    'time': birth_time,
                    'place': birth_place
                }
                st.success("✅ Birth data saved! Navigate to Birth Chart to continue.")
            else:
                st.error("Please enter your birth place.")
    
    # Session status
    st.subheader("Session Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.birth_data:
            st.success("✅ Birth data entered")
        else:
            st.info("ℹ️ No birth data yet")
    
    with col2:
        if st.session_state.chart_calculated:
            st.success("✅ Chart calculated")
        else:
            st.info("ℹ️ Chart not calculated")
    
    with col3:
        if st.session_state.predictions_generated:
            st.success("✅ Predictions ready")
        else:
            st.info("ℹ️ No predictions yet")
    
    # Features overview
    st.subheader("Available Features")
    
    features = {
        "🏠 Home": "Welcome page and quick start",
        "📊 Birth Chart": "Detailed natal chart calculation and display",
        "🔮 Predictions": "Past, present, and future life analysis", 
        "💫 Dasha Analysis": "Planetary period predictions",
        "🌟 Transit Analysis": "Current planetary influences",
        "💎 Remedies": "Personalized remedial measures",
        "📋 Reports": "Comprehensive PDF reports"
    }
    
    for feature, description in features.items():
        st.write(f"**{feature}**: {description}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>⭐ Powered by AI | Based on Classical Vedic Astrology ⭐</p>
        <p>© 2025 Vedic Astrologer App - Ancient Wisdom, Modern Technology</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
