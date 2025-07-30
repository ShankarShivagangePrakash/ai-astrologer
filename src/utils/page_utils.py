"""
Common page utilities to eliminate duplication across all pages.
This module handles common page setup, navigation, and data checks.
"""

import streamlit as st
import sys
import os

# Add project directories to path (done once for all pages)
current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)
sys.path.append(os.path.join(project_root, 'src'))
sys.path.append(os.path.join(project_root, 'components'))
sys.path.append(os.path.join(project_root, 'config'))

# Import utilities
from src.utils.ui_components import render_sidebar_navigation
from src.utils.common import get_session_value, SESSION_KEYS

def setup_page(title, icon, layout="wide"):
    """
    Standard page configuration for all pages
    """
    st.set_page_config(
        page_title=f"{title} - Vedic Astrologer",
        page_icon=icon,
        layout=layout
    )

def render_page_header(title, subtitle):
    """
    Standard page header with title and subtitle
    """
    st.title(f"{title}")
    st.markdown(f"### {subtitle}")

def check_birth_data_and_render(content_callback, page_title="this page"):
    """
    Check for birth data and render content or show warning
    
    Args:
        content_callback: Function to call if birth data exists
        page_title: Name of the current page for error message
    """
    # Always render sidebar navigation
    render_sidebar_navigation()
    
    # Check if birth data exists
    birth_data = get_session_value(SESSION_KEYS['BIRTH_DATA'], {})
    
    if birth_data:
        # Birth data exists, render the content
        st.success("✅ Birth data available for analysis!")
        
        # Show birth data summary with header
        st.subheader("📋 Birth Information")
        
        col1, col2 = st.columns(2)
        with col1:
            # Date information
            date_str = birth_data.get('date', 'Unknown')
            if hasattr(date_str, 'strftime'):
                date_str = date_str.strftime('%Y-%m-%d')
            st.write(f"**📅 Date:** {date_str}")
            
            # Location information - handle both old and new formats
            if isinstance(birth_data.get('location'), dict):
                location_data = birth_data['location']
                city = location_data.get('city', '')
                state = location_data.get('state', '')
                country = location_data.get('country', '')
                place_str = f"{city}, {state}, {country}" if state else f"{city}, {country}"
                st.write(f"**� Place:** {place_str}")
                
                # Show coordinates if available
                if coordinates := location_data.get('coordinates'):
                    st.write(f"**🌍 Latitude:** {coordinates['latitude']:.6f}°")
                    st.write(f"**🌍 Longitude:** {coordinates['longitude']:.6f}°")
                    
                    # Show formatted address if available
                    if formatted_address := coordinates.get('formatted_address'):
                        st.caption(f"*Verified as: {formatted_address}*")
            else:
                # Backward compatibility with old string format
                st.write(f"**📍 Place:** {birth_data.get('place', 'Unknown')}")
                
        with col2:
            # Time information
            time_str = birth_data.get('time', 'Unknown')
            if hasattr(time_str, 'strftime'):
                time_str = time_str.strftime('%H:%M:%S')
            st.write(f"**⏰ Time:** {time_str}")
            
            # Precise time
            if birth_data.get('hour') is not None:
                st.write(f"**🕐 Precise Time:** {birth_data.get('hour'):02d}:{birth_data.get('minute'):02d}")
            
            # Timezone offset
            if birth_data.get('timezone_offset') is not None:
                offset = birth_data['timezone_offset']
                st.write(f"**🌐 Timezone Offset:** {offset:+.1f} hours from UTC")
        
        st.markdown("---")
        content_callback(birth_data)
    else:
        # No birth data, show compact warning
        st.error("🚫 **Birth Data Required**")
        st.caption(f"To access **{page_title}**, save your birth details first.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("""
            **📝 Quick Steps:**
            1. Go to Home page
            2. Enter birth details
            3. Click Save Birth Data
            4. Return here
            """)
        
        with col2:
            st.warning("""
            **⚠️ Required for:**
            • Planetary positions
            • House placements  
            • Accurate predictions
            • Personalized analysis
            """)
        
        # Compact navigation buttons
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if st.button("🏠 Go to Home", type="primary", key=f"home_btn_{page_title}"):
                st.switch_page("streamlit_app.py")
        with nav_col2:
            if st.button("🔄 Refresh", key=f"refresh_btn_{page_title}"):
                st.rerun()

def create_birth_info_display(birth_data):
    """
    Standard birth information display component
    """
    st.subheader("📋 Birth Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**📅 Date:** {birth_data.get('date', 'Unknown')}")
        st.write(f"**📍 Place:** {birth_data.get('place', 'Unknown')}")
    
    with col2:
        st.write(f"**⏰ Time:** {birth_data.get('time', 'Unknown')}")
        if birth_data.get('hour') is not None and birth_data.get('minute') is not None:
            st.write(f"**🕐 Precise Time:** {birth_data.get('hour'):02d}:{birth_data.get('minute'):02d}")

def render_coming_soon_section(title, features_list, icon="🚧"):
    """
    Standard "coming soon" section for features under development
    """
    st.subheader(title)
    st.info(f"{icon} Feature coming soon!")
    st.write("**This section will include:**")
    for feature in features_list:
        st.write(f"- {feature}")

def render_standard_disclaimer():
    """
    Standard disclaimer for astrological content
    """
    st.markdown("---")
    st.subheader("⚠️ Important Disclaimer")
    st.warning("""
    **Please Note:**
    - These are general guidelines based on traditional Vedic astrology
    - Personal consultations provide more accurate and detailed analysis
    - Results may vary based on individual circumstances and karma
    - Always use your own judgment when making important life decisions
    """)

def create_standard_page_layout(page_config):
    """
    Create a complete page with standard layout and balanced spacing
    
    Args:
        page_config: Dictionary with page configuration
        {
            'title': 'Page Title',
            'icon': '📊', 
            'subtitle': 'Page subtitle',
            'content_callback': function_to_render_content,
            'page_id': 'unique_page_identifier'
        }
    """
    # Setup page
    setup_page(page_config['title'], page_config['icon'])
    
    # Add balanced spacing CSS for this page
    st.markdown("""
    <style>
    /* Balanced top and bottom spacing - not zero but reduced */
    .main .block-container {
        padding-top: 0.75rem !important;
        padding-bottom: 0.75rem !important;
    }
    
    /* Reduce spacing between elements while maintaining readability */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* First element should start closer to top */
    .element-container:first-child {
        margin-top: 0rem !important;
    }
    
    /* Compact headers */
    h1, h2, h3 {
        margin-top: 0.25rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Reduce alert spacing */
    .stAlert {
        margin: 0.25rem 0 0.5rem 0 !important;
        padding: 0.5rem 0.75rem !important;
    }
    
    /* Compact info boxes */
    .stInfo, .stWarning, .stError, .stSuccess {
        margin: 0.25rem 0 0.5rem 0 !important;
        padding: 0.5rem 0.75rem !important;
    }
    
    /* Compact tabs */
    .stTabs [data-baseweb="tab-list"] {
        margin-bottom: 0.5rem !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 0.5rem !important;
    }
    
    /* Compact expanders */
    .stExpander {
        margin: 0.25rem 0 0.5rem 0 !important;
    }
    
    .streamlit-expanderHeader {
        padding: 0.5rem 0.75rem !important;
    }
    
    .streamlit-expanderContent {
        padding: 0.5rem 0.75rem !important;
    }
    
    /* Compact buttons in content */
    .stButton > button {
        padding: 0.375rem 0.75rem !important;
        margin: 0.25rem 0 !important;
    }
    
    /* Reduce column spacing */
    .css-ocqkz7 {
        gap: 0.5rem !important;
    }
    
    /* Compact text inputs */
    .stTextInput {
        margin-bottom: 0.5rem !important;
    }
    
    /* Reduce form spacing */
    .stTextInput > div > div > input {
        padding: 0.375rem 0.75rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render header
    render_page_header(page_config['title'], page_config['subtitle'])
    
    # Check birth data and render content
    check_birth_data_and_render(
        page_config['content_callback'], 
        page_config.get('page_id', 'page')
    )

# Common feature lists for reuse
CHART_FEATURES = [
    "Interactive birth chart visualization",
    "Detailed planetary positions and degrees", 
    "Complete house analysis and significations",
    "Planetary aspects and yogas",
    "Chart in multiple formats (North/South Indian)"
]

PREDICTION_FEATURES = [
    "Comprehensive personality analysis",
    "Career and financial prospects",
    "Relationship and marriage timing",
    "Health and wellness guidance", 
    "Spiritual path and life purpose"
]

DASHA_FEATURES = [
    "Complete Vimshottari Dasha timeline",
    "Current Mahadasha and Antardasha analysis",
    "Major life events timing predictions",
    "Favorable and challenging period identification",
    "Remedial measures for difficult periods"
]

TRANSIT_FEATURES = [
    "Current planetary positions and influences",
    "Upcoming major transits and their effects",
    "Best timing for important decisions",
    "Monthly and yearly transit forecasts",
    "Personal transit calendar"
]

REMEDY_CATEGORIES = {
    "mantras": {
        "title": "🙏 Mantra Recommendations", 
        "general": [
            "**Gayatri Mantra**: For wisdom and spiritual growth",
            "**Mahamrityunjaya Mantra**: For health and protection", 
            "**Om Namah Shivaya**: For inner peace and transformation"
        ]
    },
    "gemstones": {
        "title": "💎 Gemstone Guidance",
        "notes": [
            "Gemstones should be recommended based on detailed chart analysis",
            "Always consult a qualified astrologer before wearing",
            "Quality, weight, and timing are crucial factors",
            "Proper purification and energization is essential"
        ]
    },
    "rituals": {
        "title": "🕯️ Ritual Suggestions", 
        "general": [
            "Daily meditation and prayer practice",
            "Offering water to Sun at sunrise",
            "Lighting oil lamps in the evening",
            "Reading spiritual texts regularly"
        ]
    },
    "donations": {
        "title": "🎁 Charitable Actions",
        "general": [
            "Feed the hungry and needy",
            "Support education for underprivileged", 
            "Plant trees and care for environment",
            "Help animals and birds in need"
        ]
    }
}
