import streamlit as st
import sys
import os

# Add paths
sys.path.append('.')
sys.path.append('src')
sys.path.append('components')

# Set page config
st.set_page_config(
    page_title="Debug Predictions",
    page_icon="🔮",
    layout="wide"
)

# Test imports
try:
    from src.utils.common import SESSION_KEYS, get_session_value
    from src.utils.page_utils import create_standard_page_layout
    # Test direct import  
    import importlib.util
    spec = importlib.util.spec_from_file_location("predictions", "pages/03_Predictions.py")
    predictions_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predictions_module)
    
    st.write("✅ All imports successful")
    
    # Check session state
    st.write("### Session State Debug")
    birth_data = get_session_value(SESSION_KEYS['BIRTH_DATA'], {})
    
    if birth_data:
        st.success(f"✅ Birth data found: {birth_data}")
    else:
        st.warning("⚠️ No birth data found - this is why predictions page appears empty!")
        st.write("**To fix this:**")
        st.write("1. Go to Home page")
        st.write("2. Enter birth date, time, and place")
        st.write("3. Click 'Save Birth Data' or 'Generate Quick Prediction'")
        st.write("4. Then return to Predictions page")
    
    st.write("### Test Predictions Main Function")
    if st.button("Run Predictions Main"):
        predictions_module.main()
        
except Exception as e:
    st.error(f"❌ Error: {e}")
    import traceback
    st.code(traceback.format_exc())
