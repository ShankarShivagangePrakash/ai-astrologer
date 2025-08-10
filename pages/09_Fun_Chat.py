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
    
    # Get method info if available
    method_info = st.session_state.get('last_rag_method', {})
    
    message_data = {
        'question': question,
        'answer': answer,
        'timestamp': timestamp
    }
    
    # Add method information if available
    if method_info:
        message_data['method'] = method_info.get('method', 'unknown')
        message_data['similarity'] = method_info.get('similarity', 0.0)
    
    st.session_state.fun_chat_messages.append(message_data)

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
            # Get method info for display
            method = msg.get('method', 'Unknown')
            similarity = msg.get('similarity', 0.0)
            
            # Choose color based on method
            if method == "ChromaDB Vector Search":
                method_icon = "🟢"
            elif method == "Wikipedia Search":
                method_icon = "🟠"
            elif method == "Llama 3.2 Response":
                method_icon = "🟣"
            elif method == "AI Assistant":
                method_icon = "🔵"
            else:
                method_icon = "⚪"
            
            # Create expander title with method info
            if method != 'Unknown':
                expander_title = f"Q{len(valid_messages) - i + 1}: {msg['question'][:40]}... {method_icon}"
            else:
                expander_title = f"Q{len(valid_messages) - i + 1}: {msg['question'][:50]}..."
            
            with st.expander(expander_title, expanded=False):
                st.write(f"**🙋 You:** {msg['question']}")
                st.write(f"**🎉 Maha Prabhu:** {msg['answer']}")
                
                # Show method and similarity if available
                if method != 'Unknown':
                    st.caption(f"**Source:** {method_icon} {method} (Similarity: {similarity:.1%})")
                
                if msg.get('timestamp'):
                    st.caption(f"*Asked: {msg['timestamp']}*")
        
        st.markdown("---")
    else:
        # Welcome message for new users
        st.info("🌟 Welcome to Fun Astro Chat! I'm Maha Prabhu, your mystical guide ready to make astrology fun and engaging! Ask me anything or just chat! ✨")
    
    # Fun suggestion list (non-clickable) - moved above question input
    # st.markdown("---")
    st.write("### 💫 Fun Question Ideas:")
    
    st.markdown("""
    - 🧙‍♂️ What is your name?
    - 💪 How can I grow in life?
    - 🧘‍♀️ How do I take out stress from my life?
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
        if st.button("🌟 Chat with Maha Prabhu!", type="primary", disabled=not user_question.strip()):
            if user_question.strip():
                with st.spinner("🌟 Consulting the cosmic wisdom..."):
                    # Get fun AI response
                    response = generate_fun_astro_response(user_question, birth_data)
                    
                    if response:
                        # Add to chat history
                        add_to_fun_chat_history(user_question, response)
                        
                        # Show the response
                        st.success("✨ Cosmic wisdom received!")
                        
                        # Display method used (if available)
                        if 'last_rag_method' in st.session_state and st.session_state.last_rag_method:
                            method_info = st.session_state.last_rag_method
                            method = method_info.get('method', 'unknown')
                            similarity = method_info.get('similarity', 0.0)
                            
                            # Color code based on method
                            if method == "ChromaDB Vector Search":
                                method_color = "🟢"
                            elif method == "Wikipedia Search":
                                method_color = "🟠"
                            elif method == "Llama 3.2 Response":
                                method_color = "🟣"
                            elif method == "AI Assistant":
                                method_color = "🔵"
                            else:
                                method_color = "⚪"
                            
                            st.info(f"{method_color} **Answer Source:** {method} (Similarity: {similarity:.1%})")
                        
                        with st.container():
                            st.write(f"**🙋 Your Question:** {user_question}")
                            st.write(f"**🎉 Maha Prabhu's Answer:**")
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
        
        # Check Multi-Method RAG system status
        system_status = "🌟 Standard AI Mode"
        system_details = "Using enhanced AI responses"
        
        try:
            from src.utils.multi_method_rag import get_multi_method_rag
            multi_rag = get_multi_method_rag()
            if multi_rag.is_available():
                system_status = "🚀 Multi-Method RAG System"
                kb_size = multi_rag.get_knowledge_base_size()
                system_details = f"ChromaDB Vector Search ({kb_size} documents)"
                st.success(f"{system_status}: Active")
                st.caption(system_details)
                
                # Show search methods
                st.write("**Search Methods:**")
                st.caption("🟢 1. ChromaDB Vector Search")
                st.caption("🟠 2. Wikipedia Search") 
                st.caption("🔵 4. AI Assistant")
                st.caption(f"**Threshold:** {multi_rag.similarity_threshold:.0%} similarity")
                
            else:
                st.warning("⚡ Basic AI Mode: Active")
                st.caption("Multi-method RAG unavailable, using standard responses")
        except ImportError:
            st.info(f"{system_status}: Active")
            st.caption(system_details)
        
        # Show last method used
        if 'last_rag_method' in st.session_state and st.session_state.last_rag_method:
            method_info = st.session_state.last_rag_method
            method = method_info.get('method', 'unknown')
            similarity = method_info.get('similarity', 0.0)
            
            st.write("**Last Answer Source:**")
            if method == "ChromaDB Vector Search":
                st.success(f"🟢 {method}")
            elif method == "Wikipedia Search":
                st.info(f"🟠 {method}")
            elif method == "Llama 3.2 Response":
                st.info(f"🔵 {method}")
            elif method == "AI Assistant":
                st.info(f"🔵 {method}")
            else:
                st.info(f"⚪ {method}")
            
            st.caption(f"Similarity: {similarity:.1%}")
        
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
    system_info = "🌟 **Fun AI Chat:** Ask me anything about astrology - I'll make it entertaining!"
    
    try:
        # Check for Multi-Method RAG
        from src.utils.multi_method_rag import get_multi_method_rag
        multi_rag = get_multi_method_rag()
        if multi_rag.is_available():
            kb_size = multi_rag.get_knowledge_base_size()
            system_info = f"🚀 **Multi-Method ChromaDB RAG:** I use 4 search methods with {multi_rag.similarity_threshold:.0%} similarity threshold!"
            st.info(system_info)
            
            # Show method details
            st.markdown(f"""
            **🔍 Search Methods (in order):**
            - 🟢 **ChromaDB Vector Search:** {kb_size} documents in vector database
            - 🟠 **Wikipedia Search:** Reliable encyclopedia knowledge
            - 🔵 **AI Assistant:** Personalized Maha Prabhu responses
            
            """)
        else:
            system_info = "🌟 **Standard AI Mode:** Ready to chat about astrology with fun personality!"
            st.info(system_info)
    except ImportError:
        system_info = "🌟 **Fun AI Chat:** Ask me anything about astrology - I'll make it entertaining!"
        st.info(system_info)
    
    # Get birth data silently (for AI use, but don't display it)
    birth_data = get_session_value(SESSION_KEYS['BIRTH_DATA'], {})
    
    # Render the main content
    render_fun_chat_content(birth_data)
    
    # Add disclaimer at the bottom
    render_standard_disclaimer()

if __name__ == "__main__":
    main()
