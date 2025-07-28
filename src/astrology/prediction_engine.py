import os
import streamlit as st
from datetime import datetime
from langchain_openai import ChatOpenAI

def setup_ai_model():
    """Setup AI model for predictions"""
    try:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            st.error("⚠️ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            return None
            
        llm = ChatOpenAI(
            model="gpt-4o", 
            api_key=OPENAI_API_KEY, 
            base_url="https://chat.expertcity.com/api"
        )
        return llm
    except Exception as e:
        st.error(f"⚠️ Error setting up AI model: {str(e)}")
        return None

def generate_quick_prediction(birth_date, birth_time, birth_place):
    """Generate quick astrological prediction using AI"""
    llm = setup_ai_model()
    if not llm:
        return "Unable to generate prediction. AI service unavailable."
    
    try:
        # Create prediction prompt
        prompt = f"""
        As a professional Vedic astrologer, provide a brief astrological insight for someone born on:
        
        Date: {birth_date.strftime('%B %d, %Y')}
        Time: {birth_time.strftime('%H:%M')}
        Place: {birth_place}
        
        Please provide:
        1. A brief personality insight based on potential planetary positions
        2. One key strength and one area for growth
        3. A positive affirmation for today
        
        Keep the response concise (under 200 words) and encouraging. Focus on general Vedic astrology principles.
        """
        
        with st.spinner("🔮 Generating your personalized prediction..."):
            response = llm.invoke(prompt)
            return response.content
            
    except Exception as e:
        return f"Unable to generate prediction at this time. Error: {str(e)}"

def generate_detailed_prediction(birth_data):
    """Generate detailed astrological prediction for comprehensive analysis"""
    llm = setup_ai_model()
    if not llm:
        return "Unable to generate detailed prediction. AI service unavailable."
    
    try:
        prompt = f"""
        As a master Vedic astrologer, provide a comprehensive astrological analysis for:
        
        Birth Date: {birth_data['date'].strftime('%B %d, %Y')}
        Birth Time: {birth_data['time'].strftime('%H:%M')}
        Birth Place: {birth_data['place']}
        
        Please provide detailed insights on:
        1. Personality and character traits
        2. Career and professional life
        3. Relationships and marriage
        4. Health and well-being
        5. Spiritual path and life purpose
        6. Major life periods and timing
        
        Base your analysis on traditional Vedic astrology principles and provide practical guidance.
        """
        
        with st.spinner("🔮 Generating comprehensive astrological analysis..."):
            response = llm.invoke(prompt)
            return response.content
            
    except Exception as e:
        return f"Unable to generate detailed prediction. Error: {str(e)}"
