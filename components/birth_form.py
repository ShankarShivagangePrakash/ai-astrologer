import streamlit as st
from datetime import datetime
from src.astrology.prediction_engine import generate_quick_prediction

def render_birth_form():
    """Render birth details input form"""
    st.subheader("Quick Start")
    
    # Show existing prediction if available
    if st.session_state.get('quick_prediction'):
        st.subheader("🔮 Your Latest Prediction")
        st.write(st.session_state.quick_prediction)
        st.markdown("---")
    
    with st.expander("Enter Birth Details (Optional)", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Date input
            today = datetime.now().date()
            min_date = datetime(today.year - 100, 1, 1).date()
            max_date = today
            
            birth_date = st.date_input(
                "Birth Date", 
                value=today,
                min_value=min_date,
                max_value=max_date,
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
        if st.button("Generate Quick Prediction", type="primary"):
            if birth_place:
                selected_time = datetime.now().replace(hour=birth_hour, minute=birth_minute, second=0, microsecond=0).time()
                
                # Store birth data in session state
                st.session_state.birth_data = {
                    'date': birth_date,
                    'time': selected_time,
                    'place': birth_place,
                    'hour': birth_hour,
                    'minute': birth_minute
                }
                
                # Generate AI prediction
                prediction = generate_quick_prediction(birth_date, selected_time, birth_place)
                st.session_state.quick_prediction = prediction
                st.session_state.predictions_generated = True
                
                st.success(f"✅ Birth data saved! Time: {birth_hour:02d}:{birth_minute:02d}")
                
                # Display the prediction
                st.subheader("🔮 Your Quick Prediction")
                st.write(prediction)
                
                st.info("💡 Navigate to other pages for detailed analysis and remedies!")
                
            else:
                st.error("Please enter your birth place.")
