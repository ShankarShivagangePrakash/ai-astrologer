import streamlit as st
from src.astrology.prediction_engine import (
    get_chat_response,
    get_chat_history,
    add_to_chat_history,
    clear_chat_history
)

def render_interactive_chat(birth_data):
    """Render interactive chat interface for astrological questions"""
    # Display chat history
    chat_messages = get_chat_history()
    
    if chat_messages:
        st.write("### 📝 Conversation History")
        
        # Display messages in reverse order (latest first)
        for i, msg in enumerate(reversed(chat_messages), 1):
            with st.expander(f"Q{len(chat_messages) - i + 1}: {msg['question'][:50]}...", expanded=(i == 1)):
                st.write(f"**🙋 Question:** {msg['question']}")
                st.write(f"**🔮 Astrologer:** {msg['answer']}")
                if msg.get('timestamp'):
                    st.caption(f"*Asked: {msg['timestamp']}*")
        
        st.markdown("---")
    
    # Question input
    st.write("### ❓ Ask Your Question")
    
    # Question input field
    user_question = st.text_input(
        "Type your question:", 
        value=st.session_state.get('suggested_question', ''),
        placeholder="e.g., What does my birth chart say about my career prospects?",
        key="user_question_input"
    )
    
    # Clear suggested question after use
    if 'suggested_question' in st.session_state:
        del st.session_state.suggested_question
    
    # Submit button
    col_submit, col_clear = st.columns([3, 1])
    with col_submit:
        if st.button("🔮 Get Answer", type="primary", key="submit_question", disabled=not user_question.strip()):
            if user_question.strip():
                with st.spinner("🔮 Consulting the stars..."):
                    # Get AI response
                    response = get_chat_response(birth_data, user_question)
                    
                    # Add to chat history
                    add_to_chat_history(user_question, response)
                    
                    # Show the response
                    st.success("✨ Response received!")
                    with st.container():
                        st.write(f"**🙋 Your Question:** {user_question}")
                        st.write(f"**🔮 Astrologer's Answer:**")
                        st.markdown(response)
                    
                    # Rerun to update chat history display
                    st.rerun()
    
    with col_clear:
        if st.button("🔄 Clear Chat", key="clear_chat_btn"):
            clear_chat_history()
            st.rerun()

def render_chat_sidebar_info():
    """Render chat information in sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.write("### 💬 Interactive Chat")
        chat_messages = get_chat_history()
        
        if chat_messages:
            st.write(f"**Questions Asked:** {len(chat_messages)}")
            st.write("**Recent Topics:**")
            for msg in chat_messages[-3:]:  # Show last 3 questions
                st.caption(f"• {msg['question'][:30]}...")
        else:
            st.write("No questions asked yet.")
            st.caption("Start a conversation to get personalized insights!")
