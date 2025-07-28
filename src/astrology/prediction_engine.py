import streamlit as st
from src.utils.common import (
    setup_ai_model,
    generate_ai_response,
    format_birth_datetime
)

def generate_quick_prediction(birth_date, birth_time, birth_place):
    """Generate quick astrological prediction using AI"""
    # Format birth data for prompt
    formatted_data = format_birth_datetime(birth_date, birth_time)
    
    prompt = f"""
    As a professional Vedic astrologer, provide a brief astrological insight for someone born on:
    
    Date: {formatted_data['date_str']}
    Time: {formatted_data['time_str']}
    Place: {birth_place}
    
    Please provide:
    1. A brief personality insight based on potential planetary positions
    2. One key strength and one area for growth
    3. A positive affirmation for today
    
    Keep the response concise (under 200 words) and encouraging. Focus on general Vedic astrology principles.
    """
    
    return generate_ai_response(prompt, "🔮 Generating your personalized prediction...")

def generate_detailed_prediction(birth_data):
    """Generate detailed astrological prediction for comprehensive analysis"""
    # Format birth data for prompt
    formatted_data = format_birth_datetime(birth_data['date'], birth_data['time'])
    
    prompt = f"""
    As a master Vedic astrologer, provide a comprehensive astrological analysis for:
    
    Birth Date: {formatted_data['date_str']}
    Birth Time: {formatted_data['time_str']}
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
    
    return generate_ai_response(prompt, "🔮 Generating comprehensive astrological analysis...")
