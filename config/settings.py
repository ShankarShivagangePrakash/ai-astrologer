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
    "model": "llama3.2:latest",
    "base_url": "http://localhost:11434",
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

def get_ollama_url():
    """Get Ollama base URL"""
    return "http://localhost:11434"

# Import environment validation from common utilities
from src.utils.common import validate_environment
