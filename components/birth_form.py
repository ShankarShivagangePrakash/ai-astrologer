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
from src.utils.location_utils import (
    render_location_inputs,
    create_location_data_dict,
    validate_location_data,
    get_location_summary,
    fetch_coordinates_for_location
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
            # Location inputs (simplified - coordinates fetched automatically)
            city, state, country = render_location_inputs()
            
        # Create helper function for processing birth data
        def process_birth_data():
            """Process and validate birth data with automatic coordinate fetching"""
            selected_time = create_time_from_components(birth_hour, birth_minute)
            
            # First validate basic inputs
            temp_location_data = create_location_data_dict(city, state, country, None)
            errors = validate_birth_inputs(birth_date, selected_time, temp_location_data)
            location_errors = validate_location_data(temp_location_data)
            errors.extend(location_errors)
            
            if render_error_messages(errors):
                return None, None, None
            
            # If validation passes, fetch coordinates automatically
            with st.spinner("🌍 Fetching location coordinates for accurate calculations..."):
                coordinates = fetch_coordinates_for_location(city, state, country)
                
                if coordinates:
                    st.success(f"✅ Location found: {coordinates['formatted_address']}")
                    st.info(f"📍 Coordinates: {coordinates['latitude']:.4f}°, {coordinates['longitude']:.4f}°")
                else:
                    st.warning("⚠️ Could not fetch coordinates automatically. Calculations will use approximate location.")
                
                # Create final location data with coordinates (if available)
                location_data = create_location_data_dict(city, state, country, coordinates)
                
                birth_data = create_birth_data_dict(
                    birth_date, selected_time, location_data, birth_hour, birth_minute
                )
                set_session_value(SESSION_KEYS['BIRTH_DATA'], birth_data)
                return birth_data, selected_time, location_data
        
        # Button layout
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            # Save Birth Data button (primary action)
            if st.button("💾 Save Birth Data", type="primary", key="save_birth_data_btn"):
                birth_data, selected_time, location_data = process_birth_data()
                if birth_data:
                    st.success(f"✅ Birth data saved! Time: {birth_hour:02d}:{birth_minute:02d}")
                    st.info("🎯 Now you can access Birth Chart, Predictions, and other features!")
                    
        with btn_col2:
            # Generate Quick Prediction button (secondary action)
            if st.button("🔮 Generate Quick Prediction", key="generate_prediction_btn"):
                birth_data, selected_time, location_data = process_birth_data()
                if birth_data:
                    # Use location string for prediction (for compatibility)
                    place_string = location_data.get('place_string', f"{city}, {country}")
                    
                    # Generate AI prediction with spinner
                    with st.spinner("🔮 Generating your personalized prediction..."):
                        prediction = generate_quick_prediction(birth_date, selected_time, place_string)
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
