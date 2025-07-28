"""
Common utility functions to avoid code duplication across the application.
This module consolidates frequently used logic patterns.
"""

import streamlit as st
import os
from datetime import datetime, time
from langchain_openai import ChatOpenAI

# =============================================================================
# DATE AND TIME UTILITIES
# =============================================================================

def get_date_range_config():
    """Get standardized date range configuration"""
    today = datetime.now().date()
    return {
        'today': today,
        'min_date': datetime(today.year - 100, 1, 1).date(),
        'max_date': today,
        'default_year': 1990
    }

def create_time_from_components(hour, minute):
    """Create time object from hour and minute components"""
    return datetime.now().replace(
        hour=hour, 
        minute=minute, 
        second=0, 
        microsecond=0
    ).time()

def format_birth_datetime(birth_date, birth_time):
    """Format birth date and time for display"""
    return {
        'date_str': birth_date.strftime('%B %d, %Y'),
        'time_str': birth_time.strftime('%H:%M'),
        'date_display': birth_date.strftime('%d/%m/%Y'),
        'time_display': birth_time.strftime('%I:%M %p')
    }

# =============================================================================
# SESSION STATE UTILITIES
# =============================================================================

def get_session_value(key, default=None):
    """Safely get session state value with default"""
    return st.session_state.get(key, default)

def set_session_value(key, value):
    """Set session state value"""
    st.session_state[key] = value

def update_session_dict(key, updates):
    """Update a dictionary in session state"""
    if key not in st.session_state:
        st.session_state[key] = {}
    st.session_state[key].update(updates)

def has_session_data(key):
    """Check if session state has non-empty data for key"""
    return bool(get_session_value(key))

# =============================================================================
# BIRTH DATA UTILITIES
# =============================================================================

def create_birth_data_dict(birth_date, birth_time, birth_place, hour=None, minute=None):
    """Create standardized birth data dictionary"""
    return {
        'date': birth_date,
        'time': birth_time,
        'place': birth_place,
        'hour': hour if hour is not None else birth_time.hour,
        'minute': minute if minute is not None else birth_time.minute,
        'timestamp': datetime.combine(birth_date, birth_time)
    }

def validate_birth_inputs(birth_date, birth_time, birth_place):
    """Comprehensive birth data validation"""
    errors = []
    
    # Date validation
    if not birth_date:
        errors.append("Birth date is required")
    elif birth_date > datetime.now().date():
        errors.append("Birth date cannot be in the future")
    
    # Time validation
    if not birth_time:
        errors.append("Birth time is required")
    
    # Place validation
    if not birth_place or len(birth_place.strip()) < 2:
        errors.append("Please enter a valid birth place (minimum 2 characters)")
    
    return errors

def get_birth_data_summary():
    """Get formatted summary of current birth data"""
    birth_data = get_session_value('birth_data', {})
    if not birth_data:
        return "No birth data saved"
    
    date_str = birth_data.get('date', 'Unknown').strftime('%d/%m/%Y') if birth_data.get('date') else 'Unknown'
    time_str = birth_data.get('time', 'Unknown').strftime('%H:%M') if birth_data.get('time') else 'Unknown'
    place_str = birth_data.get('place', 'Unknown')
    
    return f"📅 {date_str} ⏰ {time_str} 📍 {place_str}"

def is_birth_data_complete():
    """Check if complete birth data is available"""
    birth_data = get_session_value(SESSION_KEYS['BIRTH_DATA'], {})
    required_fields = ['date', 'time', 'place']
    return all(birth_data.get(field) for field in required_fields)

def clear_session_data():
    """Clear all session data (useful for starting fresh)"""
    for key in SESSION_KEYS.values():
        if key in st.session_state:
            del st.session_state[key]

# =============================================================================
# AI MODEL UTILITIES
# =============================================================================

def setup_ai_model(model_name="gpt-4o", temperature=0.7, max_tokens=1000):
    """Setup AI model with consistent configuration"""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("⚠️ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            return None
            
        llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url="https://chat.expertcity.com/api",
            temperature=temperature,
            max_tokens=max_tokens
        )
        return llm
    except Exception as e:
        st.error(f"⚠️ Error setting up AI model: {str(e)}")
        return None

def generate_ai_response(prompt, spinner_text="🔮 Generating response..."):
    """Generate AI response with error handling"""
    llm = setup_ai_model()
    if not llm:
        return "Unable to generate response. AI service unavailable."
    
    try:
        with st.spinner(spinner_text):
            response = llm.invoke(prompt)
            return response.content
    except Exception as e:
        return f"Unable to generate response at this time. Error: {str(e)}"

# =============================================================================
# UI UTILITIES
# =============================================================================

def create_status_indicator(condition, true_text, false_text, true_type="success", false_type="info"):
    """Create consistent status indicators"""
    if condition:
        getattr(st, true_type)(true_text)
    else:
        getattr(st, false_type)(false_text)

def render_error_messages(errors):
    """Display error messages consistently"""
    if errors:
        for error in errors:
            st.error(f"❌ {error}")
        return True
    return False

def create_two_column_layout():
    """Create standard two-column layout"""
    return st.columns(2)

def create_three_column_layout():
    """Create standard three-column layout"""
    return st.columns(3)

# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

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

def validate_environment():
    """Validate required environment variables and configuration"""
    issues = []
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        issues.append("OpenAI API key not found")
    
    # Add other environment checks as needed
    
    if issues:
        for issue in issues:
            st.warning(f"⚠️ {issue}")
        return False
    return True

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

# Standard session state keys
SESSION_KEYS = {
    'BIRTH_DATA': 'birth_data',
    'CHART_CALCULATED': 'chart_calculated',
    'PREDICTIONS_GENERATED': 'predictions_generated',
    'QUICK_PREDICTION': 'quick_prediction'
}

# UI Colors and styling constants
UI_COLORS = {
    'SUCCESS': '#00ff00',
    'ERROR': '#ff0000',
    'WARNING': '#ffaa00',
    'INFO': '#0066cc'
}

# Time format constants
TIME_FORMATS = {
    'DISPLAY_12H': '%I:%M %p',
    'DISPLAY_24H': '%H:%M',
    'INPUT': '%H:%M:%S'
}

# Date format constants
DATE_FORMATS = {
    'DISPLAY': '%B %d, %Y',
    'SHORT': '%d/%m/%Y',
    'INPUT': '%Y-%m-%d'
}
