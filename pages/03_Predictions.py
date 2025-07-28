import streamlit as st
from src.utils.page_utils import (
    create_standard_page_layout,
    create_birth_info_display
)
from src.utils.common import get_session_value, SESSION_KEYS
from src.astrology.prediction_engine import generate_detailed_prediction

def render_predictions_content(birth_data):
    """Render predictions specific content"""
    # Show quick prediction if available
    quick_prediction = get_session_value(SESSION_KEYS['QUICK_PREDICTION'], "")
    if quick_prediction:
        st.subheader("🌟 Quick Prediction Summary")
        st.info(quick_prediction)
        st.markdown("---")
    
    # Detailed prediction section
    st.subheader("📋 Comprehensive Analysis")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        create_birth_info_display(birth_data)
    
    with col2:
        if st.button("Generate Detailed Prediction", type="primary", key="detailed_prediction_btn"):
            with st.spinner("🔮 Generating comprehensive astrological analysis..."):
                detailed_prediction = generate_detailed_prediction(birth_data)
                st.session_state.detailed_prediction = detailed_prediction
    
    # Show detailed prediction if available
    if hasattr(st.session_state, 'detailed_prediction') and st.session_state.detailed_prediction:
        st.markdown("---")
        st.subheader("🔬 Detailed Astrological Analysis")
        
        # Use container to handle long content properly
        with st.container():
            # Display the prediction in a more readable format
            prediction_text = st.session_state.detailed_prediction
            
            # Handle potential markdown formatting
            if prediction_text:
                st.markdown(prediction_text)
            else:
                st.error("No prediction content generated. Please try again.")
        
        # Add option to regenerate
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 Regenerate Analysis", key="regen_detailed"):
                del st.session_state.detailed_prediction
                st.rerun()
        with col2:
            if st.button("💾 Save Analysis", key="save_detailed"):
                st.success("Analysis saved to session!")
                # You can implement actual saving logic here later

def main():
    page_config = {
        'title': '🔮 Astrological Predictions',
        'icon': '🔮',
        'subtitle': 'Past, Present, and Future Life Analysis',
        'content_callback': render_predictions_content,
        'page_id': 'predictions'
    }
    
    create_standard_page_layout(page_config)

if __name__ == "__main__":
    main()
