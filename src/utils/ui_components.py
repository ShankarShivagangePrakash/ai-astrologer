import streamlit as st

def render_sidebar_navigation():
    """Render sidebar navigation menu"""
    st.sidebar.title("🌟 Navigation")
    st.sidebar.markdown("---")
    
    # Navigation buttons
    if st.sidebar.button("🏠 Home", use_container_width=True):
        st.rerun()
    if st.sidebar.button("📊 Birth Chart", use_container_width=True):
        st.switch_page("pages/02_Birth_Chart.py")
    if st.sidebar.button("🔮 Predictions", use_container_width=True):
        st.switch_page("pages/03_Predictions.py")
    if st.sidebar.button("💫 Dasha Analysis", use_container_width=True):
        st.switch_page("pages/04_Dasha_Analysis.py")
    if st.sidebar.button("🌟 Transit Analysis", use_container_width=True):
        st.switch_page("pages/05_Transit_Analysis.py")
    if st.sidebar.button("💎 Remedies", use_container_width=True):
        st.switch_page("pages/06_Remedies.py")
    if st.sidebar.button("📋 Reports", use_container_width=True):
        st.switch_page("pages/07_Reports.py")

def render_header():
    """Render main header section"""
    st.title("🔮 Vedic Astrologer App")
    st.markdown("### Welcome to AI-Powered Vedic Astrology")
    st.write("Get personalized predictions based on ancient Hindu astrology combined with modern AI.")

def render_how_it_works():
    """Render how it works section"""
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

def render_session_status():
    """Render session status indicators"""
    st.subheader("Session Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.get('birth_data'):
            st.success("✅ Birth data entered")
        else:
            st.info("ℹ️ No birth data yet")
    
    with col2:
        if st.session_state.get('chart_calculated'):
            st.success("✅ Chart calculated")
        else:
            st.info("ℹ️ Chart not calculated")
    
    with col3:
        if st.session_state.get('predictions_generated'):
            st.success("✅ Predictions ready")
        else:
            st.info("ℹ️ No predictions yet")

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
