import streamlit as st
from .common import (
    get_session_value,
    has_session_data,
    SESSION_KEYS,
    create_status_indicator,
    create_three_column_layout
)

def render_sidebar_navigation():
    """Render sidebar navigation menu"""
    st.sidebar.title("🌟 Navigation")
    st.sidebar.markdown("---")
    
    # Navigation buttons with unique keys
    if st.sidebar.button("🏠 Home", use_container_width=True, key="nav_home"):
        st.switch_page("streamlit_app.py")
    if st.sidebar.button("📊 Birth Chart", use_container_width=True, key="nav_birth_chart"):
        st.switch_page("pages/02_Birth_Chart.py")
    if st.sidebar.button("🔮 Predictions", use_container_width=True, key="nav_predictions"):
        st.switch_page("pages/03_Predictions.py")
    if st.sidebar.button("💫 Dasha Analysis", use_container_width=True, key="nav_dasha"):
        st.switch_page("pages/04_Dasha_Analysis.py")
    if st.sidebar.button("🌟 Transit Analysis", use_container_width=True, key="nav_transit"):
        st.switch_page("pages/05_Transit_Analysis.py")
    if st.sidebar.button("💎 Remedies", use_container_width=True, key="nav_remedies"):
        st.switch_page("pages/06_Remedies.py")
    if st.sidebar.button("📋 Reports", use_container_width=True, key="nav_reports"):
        st.switch_page("pages/07_Reports.py")

def render_header():
    """Render main header section"""
    st.title("🔮 Vedic Astrologer App")
    st.markdown("### Welcome to AI-Powered Vedic Astrology")
    st.write("Get personalized predictions based on ancient Hindu astrology combined with modern AI.")

def render_how_it_works():
    """Render how it works section"""
    st.subheader("How It Works")
    col1, col2, col3 = create_three_column_layout()
    
    with col1:
        st.info("📅 **Step 1: Enter Birth Details**")
        st.write("Provide your birth date, time, and location for accurate calculations")
    
    with col2:
        st.success("🔮 **Step 2: Get AI Predictions**")
        st.write("Our AI analyzes your chart using traditional Vedic principles")
    
    with col3:
        st.warning("💎 **Step 3: Receive Remedies**")
        st.write("Get personalized suggestions for a better life")

def render_quick_actions():
    """Render quick action buttons for common tasks"""
    st.write("#### 🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("� View Birth Chart", key="quick_birth_chart", use_container_width=True):
            st.switch_page("pages/02_Birth_Chart.py")
    
    with col2:
        if st.button("🔮 Get Predictions", key="quick_predictions", use_container_width=True):
            st.switch_page("pages/03_Predictions.py")
    
    with col3:
        if st.button("⏰ Dasha Analysis", key="quick_dasha", use_container_width=True):
            st.switch_page("pages/04_Dasha_Analysis.py")

def render_session_status():
    """Render current session status and birth data summary"""
    from src.utils.common import get_birth_data_summary, is_birth_data_complete
    
    # Display birth data status
    st.write("### 📋 Current Session")
    
    if is_birth_data_complete():
        st.success(f"✅ Birth data saved: {get_birth_data_summary()}")
        
        # Show feature availability
        st.write("**Available Features:**")
        col1, col2 = st.columns(2)
        with col1:
            st.write("• 📊 Birth Chart Analysis")
            st.write("• 🔮 AI Predictions")
            st.write("• ⏰ Dasha Analysis")
        with col2:
            st.write("• 🌟 Transit Analysis")
            st.write("• 💊 Remedies")
            st.write("• 📄 Reports")
        
        # Quick actions
        render_quick_actions()
            
    else:
        st.warning(f"⚠️ Incomplete birth data: {get_birth_data_summary()}")
        st.info("📝 Please complete your birth information to access all features.")
        
        if st.button("➕ Enter Birth Data", key="enter_birth_data", use_container_width=True):
            st.switch_page("streamlit_app.py")

def render_features_overview():
    """Render available features overview"""
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

def render_footer():
    """Render footer section"""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>⭐ Powered by AI | Based on Classical Vedic Astrology ⭐</p>
        <p>© 2025 Vedic Astrologer App - Ancient Wisdom, Modern Technology</p>
    </div>
    """, unsafe_allow_html=True)
