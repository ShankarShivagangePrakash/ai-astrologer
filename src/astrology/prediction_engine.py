import streamlit as st
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import ConversationChain
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
    
    # Remove spinner from here as it's handled at the UI level
    return generate_ai_response(prompt)

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
    1. **Personality and Character Traits**
    2. **Career and Professional Life**
    3. **Relationships and Marriage**
    4. **Health and Well-being**
    5. **Spiritual Path and Life Purpose**
    6. **Major Life Periods and Timing**
    
    Base your analysis on traditional Vedic astrology principles and provide practical guidance.
    Format your response with clear sections and bullet points for easy reading.
    
    After this analysis, I will be available to answer any specific questions about this person's astrological chart.
    """
    
    # Remove spinner from here as it's handled at the UI level
    return generate_ai_response(prompt)

def initialize_chat_memory(birth_data):
    """Initialize conversation memory with birth chart context"""
    if 'chat_memory' not in st.session_state:
        # Create memory that remembers last 10 exchanges
        st.session_state.chat_memory = ConversationBufferWindowMemory(
            k=10,  # Remember last 10 exchanges
            return_messages=True,
            memory_key="history"
        )
        
        # Initialize with birth data context
        formatted_data = format_birth_datetime(birth_data['date'], birth_data['time'])
        context_message = f"""I am analyzing the astrological chart for someone born on:
        
Date: {formatted_data['date_str']}
Time: {formatted_data['time_str']}
Place: {birth_data['place']}

I will provide detailed Vedic astrological insights and answer questions about this birth chart."""
        
        # Add initial context to memory
        st.session_state.chat_memory.chat_memory.add_ai_message(context_message)
    
    return st.session_state.chat_memory

def create_astrology_chat_chain(birth_data):
    """Create a conversation chain for astrology chat"""
    # Initialize memory
    memory = initialize_chat_memory(birth_data)
    
    # Get the LLM
    llm = setup_ai_model()
    if not llm:
        return None
    
    # Create the prompt template with history awareness
    formatted_data = format_birth_datetime(birth_data['date'], birth_data['time'])
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", f"""You are a master Vedic astrologer providing personalized insights for:

Birth Date: {formatted_data['date_str']}
Birth Time: {formatted_data['time_str']}
Birth Place: {birth_data['place']}

Guidelines for your responses:
1. Always reference the specific birth details when relevant
2. Use traditional Vedic astrology principles
3. Provide practical, actionable guidance
4. Keep responses focused and informative
5. If asked non-astrological questions, gently redirect to astrology topics
6. Remember our conversation history to provide contextual responses
7. Use clear formatting with bullet points when appropriate

Maintain the context of this birth chart throughout our conversation."""),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    # Create the conversation chain
    chain = ConversationChain(
        llm=llm,
        prompt=prompt_template,
        memory=memory,
        verbose=False
    )
    
    return chain

def get_chat_response(birth_data, user_question):
    """Get response from the astrology chat chain"""
    try:
        # Create or get existing chain
        if 'astro_chat_chain' not in st.session_state:
            st.session_state.astro_chat_chain = create_astrology_chat_chain(birth_data)
        
        chain = st.session_state.astro_chat_chain
        if not chain:
            return "Unable to initialize chat system. Please try again."
        
        # Get response
        response = chain.predict(input=user_question)
        return response
        
    except Exception as e:
        return f"Unable to process your question at this time. Error: {str(e)}"

def clear_chat_history():
    """Clear chat history and memory"""
    if 'chat_memory' in st.session_state:
        del st.session_state.chat_memory
    if 'astro_chat_chain' in st.session_state:
        del st.session_state.astro_chat_chain
    if 'chat_messages' in st.session_state:
        del st.session_state.chat_messages

def get_chat_history():
    """Get formatted chat history for display"""
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    return st.session_state.chat_messages

def add_to_chat_history(question, answer):
    """Add question-answer pair to chat history"""
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    st.session_state.chat_messages.append({
        'question': question,
        'answer': answer,
        'timestamp': st.session_state.get('timestamp', 'Now')
    })

def generate_conversational_response(birth_data, chat_history, user_question):
    """Generate conversational AI response maintaining context and history"""
    # This function is kept for backward compatibility
    # Use get_chat_response instead for the new interactive system
    return get_chat_response(birth_data, user_question)
