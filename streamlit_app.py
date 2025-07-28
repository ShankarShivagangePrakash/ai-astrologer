import streamlit as st
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'components'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

# Import components and utilities
from config.settings import APP_CONFIG, load_custom_css, validate_environment
from src.utils.validators import initialize_session_state
from src.utils.ui_components import (
    render_sidebar_navigation, 
    render_header, 
    render_how_it_works,
    render_session_status,
    render_features_overview,
    render_footer
)
from components.birth_form import render_birth_form

# Page configuration
st.set_page_config(
    page_title=APP_CONFIG["title"],
    page_icon=APP_CONFIG["icon"],
    layout=APP_CONFIG["layout"],
    initial_sidebar_state=APP_CONFIG["sidebar_state"]
)

def main():
    """Main application function"""
    # Initialize app
    load_custom_css()
    initialize_session_state()
    validate_environment()
    
    # Render UI components
    render_sidebar_navigation()
    render_header()
    render_how_it_works()
    render_birth_form()
    render_session_status()
    render_features_overview()
    render_footer()

if __name__ == "__main__":
    main()

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
    if 'quick_prediction' not in st.session_state:
        st.session_state.quick_prediction = ""

def main():
    """Main application function"""
    # Initialize app
    load_custom_css()
    initialize_session_state()
    validate_environment()
    
    # Render UI components
    render_sidebar_navigation()
    render_header()
    render_how_it_works()
    render_birth_form()
    render_session_status()
    render_features_overview()
    render_footer()

if __name__ == "__main__":
    main()

def generate_quick_prediction(birth_date, birth_time, birth_place):
    """Generate quick astrological prediction using AI"""
    llm = setup_ai_model()
    if not llm:
        return "Unable to generate prediction. AI service unavailable."
    
    try:
        # Create prediction prompt
        prompt = f"""
        As a professional Vedic astrologer, provide a brief astrological insight for someone born on:
        
        Date: {birth_date.strftime('%B %d, %Y')}
        Time: {birth_time.strftime('%H:%M')}
        Place: {birth_place}
        
        Please provide:
        1. A brief personality insight based on potential planetary positions
        2. One key strength and one area for growth
        3. A positive affirmation for today
        
        Keep the response concise (under 200 words) and encouraging. Focus on general Vedic astrology principles.
        """
        
        with st.spinner("🔮 Generating your personalized prediction..."):
            response = llm.invoke(prompt)
            return response.content
            
    except Exception as e:
        return f"Unable to generate prediction at this time. Error: {str(e)}"

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

def render_birth_form():
    """Render birth details input form"""
    st.subheader("Quick Start")
    
    # Show existing prediction if available
    if st.session_state.quick_prediction:
        st.subheader("🔮 Your Latest Prediction")
        st.write(st.session_state.quick_prediction)
        st.markdown("---")
    
    with st.expander("Enter Birth Details (Optional)", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Date input
            today = datetime.now().date()
            min_date = datetime(today.year - 100, 1, 1).date()
            max_date = today
            
            birth_date = st.date_input(
                "Birth Date", 
                value=today,
                min_value=min_date,
                max_value=max_date,
                help="Select your birth date (supports dates up to 100 years ago)"
            )
            
            # Time input
            st.write("**Select birth time:**")
            time_col1, time_col2 = st.columns(2)
            with time_col1:
                birth_hour = st.selectbox(
                    "Hour", 
                    options=list(range(0, 24)),
                    index=0,
                    format_func=lambda x: f"{x:02d}"
                )
            with time_col2:
                birth_minute = st.selectbox(
                    "Minute", 
                    options=list(range(0, 60)),
                    index=0,
                    format_func=lambda x: f":{x:02d}"
                )
        
        with col2:
            birth_place = st.text_input("Birth Place", placeholder="e.g., New Delhi, India")
            
        # Process form submission
        if st.button("Generate Quick Prediction", type="primary"):
            if birth_place:
                selected_time = datetime.now().replace(hour=birth_hour, minute=birth_minute, second=0, microsecond=0).time()
                
                # Store birth data in session state
                st.session_state.birth_data = {
                    'date': birth_date,
                    'time': selected_time,
                    'place': birth_place,
                    'hour': birth_hour,
                    'minute': birth_minute
                }
                
                # Generate AI prediction
                prediction = generate_quick_prediction(birth_date, selected_time, birth_place)
                st.session_state.quick_prediction = prediction
                st.session_state.predictions_generated = True
                
                st.success(f"✅ Birth data saved! Time: {birth_hour:02d}:{birth_minute:02d}")
                
                # Display the prediction
                st.subheader("🔮 Your Quick Prediction")
                st.write(prediction)
                
                st.info("💡 Navigate to other pages for detailed analysis and remedies!")
                
            else:
                st.error("Please enter your birth place.")

def render_session_status():
    """Render session status indicators"""
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

def main():
    """Main application function"""
    # Initialize app
    load_custom_css()
    initialize_session_state()
    
    # Render UI components
    render_sidebar_navigation()
    render_header()
    render_how_it_works()
    render_birth_form()
    render_session_status()
    render_features_overview()
    render_footer()

if __name__ == "__main__":
    main()
