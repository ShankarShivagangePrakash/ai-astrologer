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
            
        # Create helper function for processing birth data
        def process_birth_data():
            """Process and validate birth data"""
            selected_time = create_time_from_components(birth_hour, birth_minute)
            errors = validate_birth_inputs(birth_date, selected_time, birth_place)
            
            if not render_error_messages(errors):
                birth_data = create_birth_data_dict(
                    birth_date, selected_time, birth_place, birth_hour, birth_minute
                )
                set_session_value(SESSION_KEYS['BIRTH_DATA'], birth_data)
                return birth_data, selected_time
            return None, None
        
        # Button layout
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            # Save Birth Data button (primary action)
            if st.button("💾 Save Birth Data", type="primary", key="save_birth_data_btn"):
                birth_data, selected_time = process_birth_data()
                if birth_data:
                    st.success(f"✅ Birth data saved! Time: {birth_hour:02d}:{birth_minute:02d}")
                    st.info("🎯 Now you can access Birth Chart, Predictions, and other features!")
                    
        with btn_col2:
            # Generate Quick Prediction button (secondary action)
            if st.button("🔮 Generate Quick Prediction", key="generate_prediction_btn"):
                birth_data, selected_time = process_birth_data()
                if birth_data:
                    # Generate AI prediction with spinner
                    with st.spinner("🔮 Generating your personalized prediction..."):
                        prediction = generate_quick_prediction(birth_date, selected_time, birth_place)
                        set_session_value(SESSION_KEYS['QUICK_PREDICTION'], prediction)
                        set_session_value(SESSION_KEYS['PREDICTIONS_GENERATED'], True)
                    
                    st.success(f"✅ Birth data saved! Time: {birth_hour:02d}:{birth_minute:02d}")
                    
                    # Display the prediction
                    st.subheader("🔮 Your Quick Prediction")
                    st.markdown(prediction)
                    
        # Show navigation hint after saving
        current_birth_data = get_session_value(SESSION_KEYS['BIRTH_DATA'], {})
        if current_birth_data:
            st.info("💡 Navigate to other pages using the sidebar for detailed analysis and reports!")
