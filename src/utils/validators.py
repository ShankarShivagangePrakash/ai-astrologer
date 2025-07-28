import streamlit as st
from datetime import datetime

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

def validate_birth_data(birth_date, birth_time, birth_place):
    """Validate birth data inputs"""
    errors = []
    
    # Validate date
    if not birth_date:
        errors.append("Birth date is required")
    elif birth_date > datetime.now().date():
        errors.append("Birth date cannot be in the future")
    
    # Validate time
    if not birth_time:
        errors.append("Birth time is required")
    
    # Validate place
    if not birth_place or len(birth_place.strip()) < 2:
        errors.append("Please enter a valid birth place")
    
    return errors

def validate_coordinates(latitude, longitude):
    """Validate geographic coordinates"""
    errors = []
    
    try:
        lat = float(latitude)
        lng = float(longitude)
        
        if not (-90 <= lat <= 90):
            errors.append("Latitude must be between -90 and 90")
        
        if not (-180 <= lng <= 180):
            errors.append("Longitude must be between -180 and 180")
            
    except (ValueError, TypeError):
        errors.append("Coordinates must be valid numbers")
    
    return errors
