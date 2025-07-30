"""
Birth Data Display Component
Shows saved birth data including coordinates in a nice UI format
"""

import streamlit as st
from src.utils.common import get_session_value, SESSION_KEYS

def render_birth_data_display():
    """Render a nice display of saved birth data including coordinates"""
    birth_data = get_session_value(SESSION_KEYS['BIRTH_DATA'], {})
    
    if not birth_data:
        st.info("💡 No birth data saved yet. Please enter your birth details first.")
        return False
    
    with st.container():
        st.subheader("📋 Your Birth Information")
        
        # Create columns for better layout
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📅 Birth Date",
                value=birth_data.get('date', 'Unknown').strftime('%d %b %Y') if birth_data.get('date') else 'Unknown'
            )
            
        with col2:
            st.metric(
                label="⏰ Birth Time", 
                value=birth_data.get('time', 'Unknown').strftime('%H:%M') if birth_data.get('time') else 'Unknown'
            )
            
        with col3:
            # Handle timezone offset display
            if birth_data.get('timezone_offset') is not None:
                offset = birth_data['timezone_offset']
                st.metric(
                    label="🌐 Timezone Offset",
                    value=f"{offset:+.1f} hrs from UTC"
                )
            else:
                st.metric(
                    label="🌐 Timezone",
                    value="Auto-detected"
                )
        
        # Location information
        st.markdown("---")
        
        # Handle both old and new location formats
        if isinstance(birth_data.get('location'), dict):
            location_data = birth_data['location']
            city = location_data.get('city', '')
            state = location_data.get('state', '')
            country = location_data.get('country', '')
            
            # Location display
            loc_col1, loc_col2 = st.columns(2)
            
            with loc_col1:
                place_str = f"{city}, {state}, {country}" if state else f"{city}, {country}"
                st.metric(
                    label="📍 Birth Location",
                    value=place_str
                )
                
            with loc_col2:
                if coordinates := location_data.get('coordinates'):
                    st.metric(
                        label="🌍 Coordinates",
                        value=f"{coordinates['latitude']:.4f}°, {coordinates['longitude']:.4f}°"
                    )
                    
                    # Show formatted address if available
                    if formatted_address := coordinates.get('formatted_address'):
                        st.caption(f"Verified as: {formatted_address}")
                else:
                    st.metric(
                        label="🌍 Coordinates",
                        value="Not available"
                    )
                    st.caption("⚠️ For more accurate calculations, please re-save your birth data to fetch coordinates")
        else:
            # Backward compatibility with old string format
            st.metric(
                label="📍 Birth Place",
                value=birth_data.get('place', 'Unknown')
            )
            st.caption("⚠️ Old format detected. Please re-save your birth data for enhanced accuracy")
    
    return True

def render_birth_data_summary():
    """Render a compact summary of birth data"""
    birth_data = get_session_value(SESSION_KEYS['BIRTH_DATA'], {})
    
    if not birth_data:
        return "No birth data saved"
    
    # Date and time
    date_str = birth_data.get('date', 'Unknown').strftime('%d/%m/%Y') if birth_data.get('date') else 'Unknown'
    time_str = birth_data.get('time', 'Unknown').strftime('%H:%M') if birth_data.get('time') else 'Unknown'
    
    # Location with coordinates
    if isinstance(birth_data.get('location'), dict):
        location_data = birth_data['location']
        city = location_data.get('city', '')
        country = location_data.get('country', '')
        place_str = f"{city}, {country}"
        
        if coordinates := location_data.get('coordinates'):
            coord_str = f" ({coordinates['latitude']:.2f}°, {coordinates['longitude']:.2f}°)"
        else:
            coord_str = " (no coords)"
    else:
        place_str = birth_data.get('place', 'Unknown')
        coord_str = ""
    
    return f"📅 {date_str} ⏰ {time_str} 📍 {place_str}{coord_str}"

def render_coordinates_status():
    """Show status of coordinates availability"""
    birth_data = get_session_value(SESSION_KEYS['BIRTH_DATA'], {})
    
    if not birth_data:
        return
    
    location_data = birth_data.get('location', {})
    if isinstance(location_data, dict) and location_data.get('coordinates'):
        coordinates = location_data['coordinates']
        st.success(f"✅ Coordinates available: {coordinates['latitude']:.4f}°, {coordinates['longitude']:.4f}°")
        st.info("🎯 Using precise geographical coordinates for accurate astrological calculations")
    else:
        st.warning("⚠️ No coordinates available. Calculations will use approximate location.")
        st.info("💡 Tip: Re-save your birth data to automatically fetch coordinates for better accuracy")
