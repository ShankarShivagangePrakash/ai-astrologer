"""
History-Aware RAG implementation for Fun Chat
Uses RAG.txt knowledge base with conversational memory
Uses nomic-embed-text for local embeddings without API keys
"""

import os
import streamlit as st
import subprocess
import json
import numpy as np
from typing import List
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI

class NomicEmbeddings(Embeddings):
    """Custom embeddings class using nomic-embed-text model"""
    
    def __init__(self):
        """Initialize the nomic embedding model"""
        self._check_ollama_available()
    
    def _check_ollama_available(self):
        """Check if ollama is available and nomic-embed-text model exists"""
        try:
            # Check if ollama is installed
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise Exception("Ollama is not installed or not running")
            
            # Check if nomic-embed-text model is available
            if 'nomic-embed-text' not in result.stdout:
                st.warning("⚠️ nomic-embed-text model not found. Please install it with: `ollama pull nomic-embed-text`")
                
        except subprocess.TimeoutExpired:
            raise Exception("Ollama is not responding")
        except FileNotFoundError:
            raise Exception("Ollama is not installed")
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text using nomic-embed-text"""
        try:
            # Use ollama to generate embeddings with correct API
            # Create a JSON payload for the embedding request
            import json
            import tempfile
            
            # Create temporary input for ollama
            payload = {
                "model": "nomic-embed-text",
                "prompt": text
            }
            
            # Use ollama embeddings API
            cmd = ['ollama', 'embeddings', 'nomic-embed-text']
            result = subprocess.run(
                cmd, 
                input=text, 
                text=True,
                capture_output=True, 
                timeout=30
            )
            
            if result.returncode != 0:
                # Try alternative approach with API call
                cmd_alt = ['curl', '-X', 'POST', 'http://localhost:11434/api/embeddings',
                          '-H', 'Content-Type: application/json',
                          '-d', json.dumps(payload)]
                
                result = subprocess.run(cmd_alt, capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    return self._fallback_embedding(text)
            
            # Parse the embedding result
            try:
                if result.stdout.strip():
                    embedding_data = json.loads(result.stdout)
                    if 'embedding' in embedding_data:
                        return embedding_data['embedding']
                    elif isinstance(embedding_data, list):
                        return embedding_data
                
                return self._fallback_embedding(text)
                
            except json.JSONDecodeError:
                return self._fallback_embedding(text)
                
        except subprocess.TimeoutExpired:
            return self._fallback_embedding(text)
        except Exception as e:
            st.warning(f"Embedding error: {e}")
            return self._fallback_embedding(text)
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """Simple fallback embedding based on text hash"""
        # Create a simple hash-based embedding as fallback
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to float array (384 dimensions to match typical embedding size)
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i:i+4]
            if len(chunk) == 4:
                val = int.from_bytes(chunk, 'big') / (2**32)
                embedding.append(val)
        
        # Pad or truncate to 384 dimensions
        while len(embedding) < 384:
            embedding.extend(embedding[:min(len(embedding), 384-len(embedding))])
        
        return embedding[:384]
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        embeddings = []
        for text in texts:
            embedding = self._get_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        return self._get_embedding(text)

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
            st.info("🔧 Initializing RAG system...")
            
            # Initialize local embeddings (no API key needed)
            st.info("📡 Setting up nomic-embed-text embeddings...")
            self.embeddings = NomicEmbeddings()
            st.success("✅ Embeddings ready")
            
            # Get OpenAI API key from environment or Streamlit secrets for LLM
            api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
            if api_key:
                # Initialize OpenAI LLM for chat completion
                st.info("🤖 Setting up OpenAI LLM...")
                self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.7)
                st.success("✅ LLM ready")
            else:
                st.info("🌟 Using local RAG without OpenAI LLM. Responses will be based on knowledge base similarity.")
                self.llm = None
            
            # Load and process RAG.txt
            st.info("📚 Loading knowledge base...")
            self._load_knowledge_base()
            
            if self.vector_store:
                st.success("✅ Knowledge base loaded")
                
                # Create history-aware chain (if LLM available) or simple retrieval
                if self.llm:
                    st.info("🔗 Creating history-aware chain...")
                    self._create_history_aware_chain()
                else:
                    st.info("🔍 Setting up simple retrieval...")
                    self._create_simple_retrieval()
                
                if self.chain_with_history:
                    st.success("🎉 RAG system fully initialized!")
                else:
                    st.error("❌ Failed to create RAG chain")
            else:
                st.error("❌ Failed to load knowledge base")
            
        except Exception as e:
            st.error(f"Failed to initialize RAG system: {str(e)}")
            # Set embeddings to None to indicate failure
            self.embeddings = None
    
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
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
            self.vector_store = None
    
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
    
    def _create_simple_retrieval(self):
        """Create simple retrieval without LLM for local-only mode"""
        if not self.vector_store:
            return
        
        try:
            # Create simple retriever for knowledge base lookup
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            # Mark as available even without full RAG chain
            self.chain_with_history = "simple_retrieval"
            
        except Exception as e:
            st.error(f"Failed to create simple retrieval: {str(e)}")
    
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
                
                birth_context = f"User born on {birth_data['date']} at {birth_data.get('time', 'unknown time')} in {location_str}."
            else:
                birth_context = ""
            
            # Check if we have full RAG or simple retrieval
            if self.chain_with_history == "simple_retrieval":
                return self._get_simple_retrieval_response(question, birth_context)
            else:
                # Full RAG with LLM
                full_question = f"{birth_context}\n\nQuestion: {question}" if birth_context else question
                
                response = self.chain_with_history.invoke(
                    {"input": full_question},
                    {"configurable": {"session_id": session_id}}
                )
                
                return response.get('answer', self._fallback_response(question, birth_data))
            
        except Exception as e:
            st.error(f"RAG system error: {str(e)}")
            return self._fallback_response(question, birth_data)
    
    def _get_simple_retrieval_response(self, question: str, birth_context: str) -> str:
        """Get response using simple retrieval without LLM"""
        try:
            # Search for relevant documents
            docs = self.retriever.get_relevant_documents(question)
            
            if docs:
                # Find the most relevant answer from the knowledge base
                best_match = docs[0].page_content
                
                # Format the response in a fun way
                response = f"🌟 Found this cosmic wisdom for you! ✨\n\n{best_match}\n\n"
                
                if birth_context:
                    response += f"💫 Considering your birth details: {birth_context}\n\n"
                
                response += "🚀 This wisdom comes from Maha Prabhu's knowledge base! Ask me more questions to explore further! 🌙"
                
                return response
            else:
                return self._fallback_response(question, None)
                
        except Exception as e:
            return f"🌙 Error accessing knowledge base: {str(e)}"
    
    def _fallback_response(self, question: str, birth_data=None) -> str:
        """Fallback response when RAG system fails"""
        return """🌟 Oops! My cosmic connection seems a bit fuzzy right now! ✨ 

        Let me tell you something fun while I reconnect to the astral plane: Did you know that astrology has been guiding humans for over 4,000 years? 🌙 

        The ancient Babylonians were the first to map the stars and create the zodiac system we still use today! Pretty cosmic, right? 🌌

        Try asking me again, or ask about zodiac signs, planetary influences, or fun astrology facts! 🚀"""
    
    def is_available(self) -> bool:
        """Check if RAG system is properly initialized"""
        return self.chain_with_history is not None and self.embeddings is not None

# Global instance for Fun Chat
_fun_chat_rag = None

def get_fun_chat_rag() -> FunChatRAG:
    """Get or create the Fun Chat RAG instance"""
    global _fun_chat_rag
    if _fun_chat_rag is None:
        _fun_chat_rag = FunChatRAG()
    return _fun_chat_rag
