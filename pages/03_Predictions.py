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
    
    # Create tabs for different prediction modes
    tab1, tab2 = st.tabs(["📋 Detailed Analysis", "💬 Interactive Chat"])
    
    with tab1:
        render_detailed_prediction_tab(birth_data)
    
    with tab2:
        render_interactive_chat(birth_data)

def render_detailed_prediction_tab(birth_data):
    """Render the detailed prediction tab"""
    st.subheader("📋 Comprehensive Astrological Analysis")
    st.write("Get a complete written analysis of your birth chart covering all major life areas.")
    
    # Center the generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Generate Detailed Analysis", type="primary", key="detailed_prediction_btn"):
            with st.spinner("🔮 Generating comprehensive astrological analysis..."):
                detailed_prediction = generate_detailed_prediction(birth_data)
                st.session_state.detailed_prediction = detailed_prediction
    
    # Show detailed prediction if available
    if hasattr(st.session_state, 'detailed_prediction') and st.session_state.detailed_prediction:
        st.markdown("---")
        st.subheader("🔬 Your Detailed Astrological Analysis")
        
        # Use container to handle long content properly
        with st.container():
            # Display the prediction in a more readable format
            prediction_text = st.session_state.detailed_prediction
            
            # Handle potential markdown formatting
            if prediction_text:
                st.markdown(prediction_text)
            else:
                st.error("No prediction content generated. Please try again.")
        
        # Add option to regenerate and navigate to chat
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🔄 Regenerate Analysis", key="regen_detailed"):
                del st.session_state.detailed_prediction
                st.rerun()
        with col2:
            if st.button("💾 Save Analysis", key="save_detailed"):
                st.success("Analysis saved to session!")
        with col3:
            st.info("💡 Switch to the 'Interactive Chat' tab to ask specific questions!")

def main():
    page_config = {
        'title': '🔮 Astrological Predictions',
        'icon': '🔮',
        'subtitle': 'Comprehensive Analysis & Interactive Chat',
        'content_callback': render_predictions_content,
        'page_id': 'predictions'
    }
    
    create_standard_page_layout(page_config)

if __name__ == "__main__":
    main()
