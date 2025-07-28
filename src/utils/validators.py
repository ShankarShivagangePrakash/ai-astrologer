"""
Data validation functions.
Note: Common validation logic has been moved to src/utils/common.py
This module now contains application-specific validators.
"""
import streamlit as st
from .common import (
    set_session_value,
    SESSION_KEYS,
    validate_coordinates as common_validate_coordinates,
    validate_birth_inputs as common_validate_birth_inputs
)

def initialize_session_state():
    """Initialize session state variables"""
    # Initialize all required session state keys
    session_defaults = {
        SESSION_KEYS['BIRTH_DATA']: {},
        SESSION_KEYS['CHART_CALCULATED']: False,
        SESSION_KEYS['PREDICTIONS_GENERATED']: False,
        SESSION_KEYS['QUICK_PREDICTION']: ""
    }
    
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            set_session_value(key, default_value)

# Re-export commonly used validation functions from common module
validate_birth_data = common_validate_birth_inputs
validate_coordinates = common_validate_coordinates
