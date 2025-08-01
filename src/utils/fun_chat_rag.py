"""
History-Aware RAG implementation for Fun Chat
Uses RAG.txt knowledge base with conversational memory
"""

import os
import streamlit as st
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

class FunChatRAG:
    def __init__(self):
        self.embeddings = None
        self.llm = None
        self.chain_with_history = None
        self.vector_store = None
        self._initialize_rag()
    
    def _initialize_rag(self):
        """Initialize the RAG system with Fun Chat configuration"""
        try:
            # Get OpenAI API key from environment or Streamlit secrets
            api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
            if not api_key:
                st.error("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
                return
            
            # Initialize OpenAI components
            self.embeddings = OpenAIEmbeddings(api_key=api_key)
            self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.7)
            
            # Load and process RAG.txt
            self._load_knowledge_base()
            
            # Create history-aware chain
            self._create_history_aware_chain()
            
        except Exception as e:
            st.error(f"Failed to initialize RAG system: {str(e)}")
    
    def _load_knowledge_base(self):
        """Load and process the RAG.txt knowledge base"""
        try:
            # Load RAG.txt from assets/resources
            rag_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "assets", "resources", "RAG.txt"
            )
            
            if not os.path.exists(rag_file_path):
                st.error(f"RAG.txt not found at {rag_file_path}")
                return
            
            # Load document
            loader = TextLoader(rag_file_path)
            documents = loader.load()
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,     # Smaller chunks for Q&A pairs
                chunk_overlap=50    # Minimal overlap for Q&A format
            )
            chunks = text_splitter.split_documents(documents)
            
            # Create vector store
            self.vector_store = Chroma.from_documents(chunks, self.embeddings)
            
        except Exception as e:
            st.error(f"Failed to load knowledge base: {str(e)}")
    
    def _create_history_aware_chain(self):
        """Create the history-aware RAG chain"""
        if not self.vector_store or not self.llm:
            return
        
        try:
            # Create retriever
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            
            # Create history-aware prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are a fun, engaging, and wise Vedic astrology chatbot with a playful personality named Cosmic Buddy. 
                You have access to a knowledge base with questions and answers from an experienced astrologer.
                
                Use the provided context to answer questions, but enhance the responses with your fun personality:
                1. Be entertaining, conversational, and use lots of emojis
                2. Add creative analogies and storytelling 
                3. Keep the core astrological wisdom but make it engaging
                4. If the context doesn't have the answer, provide general fun astrological insights
                5. Always maintain a light-hearted but respectful tone
                
                Context from knowledge base:
                {context}
                """),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
            
            # Create history-aware retriever
            history_aware_retriever = create_history_aware_retriever(
                self.llm, retriever, prompt_template
            )
            
            # Create document chain
            qa_chain = create_stuff_documents_chain(self.llm, prompt_template)
            
            # Create RAG chain
            rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)
            
            # Create chain with history
            self.chain_with_history = RunnableWithMessageHistory(
                rag_chain,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history"
            )
            
        except Exception as e:
            st.error(f"Failed to create RAG chain: {str(e)}")
    
    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get chat history for a specific session"""
        if "fun_chat_rag_history" not in st.session_state:
            st.session_state.fun_chat_rag_history = {}
        
        if session_id not in st.session_state.fun_chat_rag_history:
            st.session_state.fun_chat_rag_history[session_id] = StreamlitChatMessageHistory(
                key=f"chat_messages_{session_id}"
            )
        
        return st.session_state.fun_chat_rag_history[session_id]
    
    def get_response(self, question: str, birth_data=None, session_id="fun_chat_default") -> str:
        """Get RAG-enhanced response for Fun Chat"""
        if not self.chain_with_history:
            return self._fallback_response(question, birth_data)
        
        try:
            # Add birth data context if available
            enhanced_question = question
            if birth_data and birth_data.get('date'):
                location_info = birth_data.get('location', {})
                if isinstance(location_info, dict):
                    city = location_info.get('city', '')
                    state = location_info.get('state', '')
                    country = location_info.get('country', '')
                    location_str = f"{city}, {state}, {country}" if state else f"{city}, {country}"
                else:
                    location_str = birth_data.get('place', 'Not specified')
                
                enhanced_question = f"""User's Birth Info: Born on {birth_data['date']} at {birth_data.get('time', 'unknown time')} in {location_str}
                
                Question: {question}"""
            
            # Get response from RAG chain
            response = self.chain_with_history.invoke(
                {"input": enhanced_question},
                {"configurable": {"session_id": session_id}}
            )
            
            return response.get('answer', self._fallback_response(question, birth_data))
            
        except Exception as e:
            st.error(f"RAG system error: {str(e)}")
            return self._fallback_response(question, birth_data)
    
    def _fallback_response(self, question: str, birth_data=None) -> str:
        """Fallback response when RAG system fails"""
        return """🌟 Oops! My cosmic connection seems a bit fuzzy right now! ✨ 

        Let me tell you something fun while I reconnect to the astral plane: Did you know that astrology has been guiding humans for over 4,000 years? 🌙 

        The ancient Babylonians were the first to map the stars and create the zodiac system we still use today! Pretty cosmic, right? 🌌

        Try asking me again, or ask about zodiac signs, planetary influences, or fun astrology facts! 🚀"""
    
    def is_available(self) -> bool:
        """Check if RAG system is properly initialized"""
        return self.chain_with_history is not None

# Global instance for Fun Chat
_fun_chat_rag = None

def get_fun_chat_rag() -> FunChatRAG:
    """Get or create the Fun Chat RAG instance"""
    global _fun_chat_rag
    if _fun_chat_rag is None:
        _fun_chat_rag = FunChatRAG()
    return _fun_chat_rag
