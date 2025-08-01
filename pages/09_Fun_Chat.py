import streamlit as st
from src.utils.page_utils import (
    render_standard_disclaimer
)
from src.utils.common import generate_fun_chat_rag_response, get_session_value, SESSION_KEYS
from src.utils.ui_components import render_sidebar_navigation

def generate_fun_astro_response(user_question, birth_data=None):
    """Generate fun and engaging astrology-themed responses with RAG enhancement"""
    # Use the new RAG-enhanced response function
    return generate_fun_chat_rag_response(user_question, birth_data)

def get_fun_chat_history():
    """Get fun chat history from session state"""
    messages = st.session_state.get('fun_chat_messages', [])
    # Clean up any invalid messages from old format
    valid_messages = [msg for msg in messages if isinstance(msg, dict) and 'question' in msg and 'answer' in msg]
    
    # If we had to filter out invalid messages, update the session state
    if len(valid_messages) != len(messages):
        st.session_state.fun_chat_messages = valid_messages
    
    return valid_messages

def add_to_fun_chat_history(question, answer):
    """Add message to fun chat history"""
    if 'fun_chat_messages' not in st.session_state:
        st.session_state.fun_chat_messages = []
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    st.session_state.fun_chat_messages.append({
        'question': question,
        'answer': answer,
        'timestamp': timestamp
    })

def clear_fun_chat_history():
    """Clear fun chat history"""
    st.session_state.fun_chat_messages = []

def render_fun_chat(birth_data):
    """Render interactive fun chat interface similar to Astro Chat"""
    # Initialize session state for input clearing
    if 'fun_input_counter' not in st.session_state:
        st.session_state.fun_input_counter = 0
    
    # Add custom CSS for fun chat styling
    st.markdown("""
    <style>
    /* Fun chat styling */
    .stTabs [data-baseweb="tab-panel"] > div {
        padding-top: 0.25rem !important;
    }
    
    /* Compact the expanders */
    .stExpander summary {
        padding: 0.375rem 0.75rem !important;
    }
    
    /* Reduce spacing in content */
    .stVerticalBlock {
        gap: 0.5rem !important;
    }
    
    /* Make buttons more compact */
    button[data-testid="stBaseButton-secondary"] {
        padding: 0.25rem 0.5rem !important;
        font-size: 0.875rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display chat history
    chat_messages = get_fun_chat_history()
    
    # Filter out messages that don't have the expected structure
    valid_messages = [msg for msg in chat_messages if isinstance(msg, dict) and 'question' in msg and 'answer' in msg]
    
    if valid_messages:
        st.write("### 🌟 Fun Conversation History")
        
        # Display messages in reverse order (latest first)
        for i, msg in enumerate(reversed(valid_messages), 1):
            with st.expander(f"Q{len(valid_messages) - i + 1}: {msg['question'][:50]}...", expanded=False):
                st.write(f"**🙋 You:** {msg['question']}")
                st.write(f"**🎉 Cosmic Buddy:** {msg['answer']}")
                if msg.get('timestamp'):
                    st.caption(f"*Asked: {msg['timestamp']}*")
        
        st.markdown("---")
    else:
        # Welcome message for new users
        st.info("🌟 Welcome to Fun Astro Chat! I'm your cosmic buddy ready to make astrology fun and engaging! Ask me anything about the stars, planets, or just chat! ✨")
    
    # Fun suggestion list (non-clickable) - moved above question input
    # st.markdown("---")
    st.write("### 💫 Fun Question Ideas:")
    
    st.markdown("""
    - 🌟 What's my cosmic vibe today?
    - 🚀 Tell me a fun astrology fact!
    - 💫 What do the stars say about me today?
    - 🌙 How do moon phases affect me?
    - ⭐ What's my zodiac sign's superpower?
    - 🔮 Can you read my planetary influences?
    - 🌌 Tell me about my birth chart personality
    - 💎 What gemstone suits my energy?
    - 🕉️ What rituals would help me?
    - 🎭 How do I vibe with other signs?
    - 🧙‍♂️ What is your name? (Try this for special wisdom!)
    - 💪 How can I grow in life?
    - 🧘‍♀️ How do I take out stress from my life?
    - 🏥 How can I improve my health?
    """)
    
    
    st.markdown("---")
    # Question input
    st.write("### 💫 Ask Me Anything!")
    
    # Question input field with dynamic key for clearing
    user_question = st.text_input(
        "What's on your cosmic mind?", 
        value=st.session_state.get('fun_suggested_question', ''),
        placeholder="e.g., What's my cosmic vibe today? Tell me a fun astro fact!",
        key=f"fun_user_question_input_{st.session_state.fun_input_counter}"
    )
    
    # Clear suggested question after use
    if 'fun_suggested_question' in st.session_state:
        del st.session_state.fun_suggested_question
    
    # Submit and clear buttons
    col_submit, col_clear = st.columns([3, 1])
    with col_submit:
        if st.button("🌟 Chat with Cosmic Buddy!", type="primary", disabled=not user_question.strip()):
            if user_question.strip():
                with st.spinner("🌟 Consulting the cosmic wisdom..."):
                    # Get fun AI response
                    response = generate_fun_astro_response(user_question, birth_data)
                    
                    if response:
                        # Add to chat history
                        add_to_fun_chat_history(user_question, response)
                        
                        # Show the response
                        st.success("✨ Cosmic wisdom received!")
                        with st.container():
                            st.write(f"**🙋 Your Question:** {user_question}")
                            st.write(f"**🎉 Cosmic Buddy's Answer:**")
                            st.markdown(response)
                        
                        # Clear the input by incrementing counter
                        st.session_state.fun_input_counter += 1
                        
                        # Rerun to update chat history display
                        st.rerun()
                    else:
                        st.error("🌙 Oops! The cosmic signals seem a bit fuzzy right now. Try asking again! ✨")
    
    with col_clear:
        if st.button("🔄 Clear Chat"):
            clear_fun_chat_history()
            st.rerun()

def render_fun_chat_sidebar_info():
    """Render fun chat information in sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.write("### 🎉 Fun Astro Chat")
        
        # Check RAG system status
        try:
            from src.utils.fun_chat_rag import get_fun_chat_rag
            rag_system = get_fun_chat_rag()
            if rag_system.is_available():
                st.success("🧠 RAG Knowledge Base: Active")
                st.caption("Using Maha Prabhu's wisdom from knowledge base")
            else:
                st.warning("⚡ Basic AI Mode: Active")
                st.caption("RAG system unavailable, using standard responses")
        except Exception:
            st.info("🌟 Standard AI Mode: Active")
            st.caption("Using enhanced AI responses")
        
        chat_messages = get_fun_chat_history()
        
        # Filter out messages that don't have the expected structure
        valid_messages = [msg for msg in chat_messages if isinstance(msg, dict) and 'question' in msg]
        
        if valid_messages:
            st.write(f"**Fun Questions Asked:** {len(valid_messages)}")
            st.write("**Recent Fun Topics:**")
            for msg in valid_messages[-3:]:  # Show last 3 questions
                st.caption(f"🌟 {msg['question'][:25]}...")
        else:
            st.write("No fun questions yet!")
            st.caption("🚀 Start chatting for cosmic fun!")

def render_fun_chat_content(birth_data):
    """Render fun chat specific content with optimized spacing"""
    # Add fun chat sidebar info
    render_fun_chat_sidebar_info()
    
    # Render the fun interactive chat
    render_fun_chat(birth_data)

def main():
    # Set page config
    st.set_page_config(
        page_title="🎉 Fun Astro Chat",
        page_icon="🎉",
        layout="wide"
    )
    
    # Render sidebar navigation
    render_sidebar_navigation()
    
    # Page header without birth data display
    st.title("🎉 Fun Astro Chat")
    st.markdown("### Chat with Maha Prabhu's AI Wisdom in a Fun Way!")
    
    # Add RAG status info
    try:
        from src.utils.fun_chat_rag import get_fun_chat_rag
        rag_system = get_fun_chat_rag()
        if rag_system.is_available():
            st.info("🧠 **Enhanced with Knowledge Base:** I'm powered by Maha Prabhu's wisdom and can remember our conversation!")
        else:
            st.info("🌟 **Standard AI Mode:** Ready to chat about astrology with fun personality!")
    except Exception:
        st.info("🌟 **Fun AI Chat:** Ask me anything about astrology - I'll make it entertaining!")
    
    # Get birth data silently (for AI use, but don't display it)
    birth_data = get_session_value(SESSION_KEYS['BIRTH_DATA'], {})
    
    # Render the main content
    render_fun_chat_content(birth_data)
    
    # Add disclaimer at the bottom
    render_standard_disclaimer()

if __name__ == "__main__":
    main()
