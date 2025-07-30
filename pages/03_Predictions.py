import streamlit as st
from src.utils.page_utils import (
    create_standard_page_layout,
    create_birth_info_display
)
from src.utils.common import get_session_value, SESSION_KEYS
from src.astrology.prediction_engine import generate_detailed_prediction
from components.interactive_chat import render_interactive_chat, render_chat_sidebar_info

def render_predictions_content(birth_data):
    """Render predictions specific content with optimized spacing"""
    # Add additional CSS for this specific page
    st.markdown("""
    <style>
    /* Additional spacing optimizations for Predictions page */
    .stTabs [data-baseweb="tab-panel"] > div {
        padding-top: 0.25rem !important;
    }
    
    /* Compact the birth data expander */
    .stExpander summary {
        padding: 0.375rem 0.75rem !important;
    }
    
    /* Reduce spacing in tab content */
    .stTabs .stVerticalBlock {
        gap: 0.5rem !important;
    }
    
    /* Make buttons more compact */
    button[data-testid="stBaseButton-secondary"] {
        padding: 0.25rem 0.5rem !important;
        font-size: 0.875rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add chat sidebar info
    render_chat_sidebar_info()
    
    # Show quick prediction if available
    quick_prediction = get_session_value(SESSION_KEYS['QUICK_PREDICTION'], "")
    if quick_prediction:
        st.subheader("🌟 Quick Prediction Summary")
        st.info(quick_prediction)
        st.markdown("---")
    
    # Render interactive chat directly
    render_interactive_chat(birth_data)

def main():
    page_config = {
        'title': '💬 Talk to Astrologer',
        'icon': '💬',
        'subtitle': 'Interactive Astrological Consultation & Chat',
        'content_callback': render_predictions_content,
        'page_id': 'predictions'
    }
    
    create_standard_page_layout(page_config)

if __name__ == "__main__":
    main()
