import streamlit as st
from src.astrology.prediction_engine import generate_quick_prediction
from src.utils.common import (
    get_date_range_config,
    create_time_from_components,
    create_birth_data_dict,
    validate_birth_inputs,
    set_session_value,
    get_session_value,
    SESSION_KEYS,
    render_error_messages
)

def render_birth_form():
    """Render birth details input form"""
    st.subheader("Quick Start")
    
    # Show existing prediction if available
    if get_session_value(SESSION_KEYS['QUICK_PREDICTION']):
        st.subheader("🔮 Your Latest Prediction")
        st.write(get_session_value(SESSION_KEYS['QUICK_PREDICTION']))
        st.markdown("---")
    
    with st.expander("Enter Birth Details", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Date input using utility
            date_config = get_date_range_config()
            
            birth_date = st.date_input(
                "Birth Date", 
                value=date_config['today'],
                min_value=date_config['min_date'],
                max_value=date_config['max_date'],
                help="Select your birth date (supports dates up to 100 years ago)"
            )
            
            # Time input
            st.write("**Select birth time:**")
            time_col1, time_col2 = st.columns(2)
            with time_col1:
                birth_hour = st.selectbox(
                    "Hour", 
                    options=list(range(0, 24)),
                    index=0,
                    format_func=lambda x: f"{x:02d}"
                )
            with time_col2:
                birth_minute = st.selectbox(
                    "Minute", 
                    options=list(range(0, 60)),
                    index=0,
                    format_func=lambda x: f":{x:02d}"
                )
        
        with col2:
            birth_place = st.text_input("Birth Place", placeholder="e.g., New Delhi, India")
            
        # Process form submission
        if st.button("Generate Quick Prediction", type="primary", key="birth_form_submit"):
            # Create time object using utility
            selected_time = create_time_from_components(birth_hour, birth_minute)
            
            # Validate inputs using utility
            errors = validate_birth_inputs(birth_date, selected_time, birth_place)
            
            if not render_error_messages(errors):
                # Create birth data using utility
                birth_data = create_birth_data_dict(
                    birth_date, selected_time, birth_place, birth_hour, birth_minute
                )
                
                # Store in session using utility
                set_session_value(SESSION_KEYS['BIRTH_DATA'], birth_data)
                
                # Generate AI prediction
                prediction = generate_quick_prediction(birth_date, selected_time, birth_place)
                set_session_value(SESSION_KEYS['QUICK_PREDICTION'], prediction)
                set_session_value(SESSION_KEYS['PREDICTIONS_GENERATED'], True)
                
                st.success(f"✅ Birth data saved! Time: {birth_hour:02d}:{birth_minute:02d}")
                
                # Display the prediction
                st.subheader("🔮 Your Quick Prediction")
                st.write(prediction)
                
                st.info("💡 Navigate to other pages for detailed analysis and remedies!")
