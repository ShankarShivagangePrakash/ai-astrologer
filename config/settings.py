import streamlit as st
import os

# Application Configuration
APP_CONFIG = {
    "title": "Vedic Astrologer",
    "icon": "🔮",
    "layout": "wide",
    "sidebar_state": "expanded"
}

# AI Configuration
AI_CONFIG = {
    "model": "gpt-4o",
    "base_url": "https://chat.expertcity.com/api",
    "temperature": 0.7,
    "max_tokens": 1000
}

# Date Configuration
DATE_CONFIG = {
    "max_years_back": 100,
    "default_birth_year": 1990
}

def load_custom_css():
    """Load custom CSS styling"""
    try:
        with open('assets/styles/custom.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # CSS file not found, continue without custom styling
        pass

def get_api_key():
    """Get OpenAI API key from environment"""
    return os.getenv("OPENAI_API_KEY")

def validate_environment():
    """Validate required environment variables"""
    api_key = get_api_key()
    if not api_key:
        st.warning("⚠️ OpenAI API key not found. Please set OPENAI_API_KEY environment variable for AI features.")
        return False
    return True
