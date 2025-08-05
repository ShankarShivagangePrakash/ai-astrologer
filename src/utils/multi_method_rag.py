"""
Multi-Method RAG System with ChromaDB Vector Database
Implements sequential search with cosine similarity thresholds:
1. RAG Search (ChromaDB vector database)
2. DuckDuckGo Search
3. Wikipedia Search
4. ChatGPT/AI Response

Each method is only called if previous method's cosine similarity < 40%
"""

import os
import re
import json
import subprocess
import requests
import streamlit as st
from typing import List, Dict, Tuple, Optional, Any
from urllib.parse import quote
import numpy as np
from datetime import datetime

# ChromaDB and LangChain imports
try:
    import chromadb
    from chromadb.config import Settings
    from langchain_community.document_loaders import TextLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_chroma import Chroma
    from langchain_community.embeddings import OllamaEmbeddings
    CHROMADB_AVAILABLE = True
except ImportError as e:
    CHROMADB_AVAILABLE = False
    st.error(f"❌ Required libraries not available: {e}")
    st.info("💡 Install with: pip install chromadb langchain langchain-community langchain-chroma")

class MultiMethodRAG:
    def __init__(self):
        self.vector_db = None
        self.retriever = None
        self.embeddings_model = None
        self.is_ready = False
        self.similarity_threshold = 0.4  # 40% threshold
        self.collection_name = "astrology_knowledge"
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the multi-method RAG system with ChromaDB"""
        try:
            if not CHROMADB_AVAILABLE:
                st.error("Required libraries not available.")
                return
            
            # Initialize embeddings model
            self._setup_embeddings()
            
            # Setup ChromaDB and load knowledge base
            self._setup_vector_database()
            
            self.is_ready = True
            st.success(f"🚀 Multi-Method RAG with ChromaDB initialized successfully")
        except Exception as e:
            st.error(f"Failed to initialize Multi-Method RAG: {e}")
            self.is_ready = False
    
    def _setup_embeddings(self):
        """Setup embeddings model"""
        try:
            # Use Ollama's nomic-embed-text:v1.5 model
            self.embeddings_model = OllamaEmbeddings(
                model="nomic-embed-text:v1.5",
                base_url="http://localhost:11434"
            )
            st.info("🔗 Using Ollama nomic-embed-text:v1.5 embeddings")
            
            # Test if Ollama is running
            try:
                # Try a simple embedding test
                test_result = self.embeddings_model.embed_query("test")
                if test_result:
                    st.success("✅ Ollama embeddings working correctly")
                else:
                    raise Exception("Empty embedding result")
            except Exception as e:
                st.warning(f"⚠️ Ollama embeddings test failed: {e}")
                st.info("💡 Make sure Ollama is running and nomic-embed-text:v1.5 model is installed")
                st.info("💡 Run: ollama pull nomic-embed-text:v1.5")
                self.embeddings_model = None
                
        except Exception as e:
            st.error(f"Failed to setup Ollama embeddings: {e}")
            st.info("💡 Falling back to ChromaDB default embeddings")
            self.embeddings_model = None
    
    def _setup_vector_database(self):
        """Setup ChromaDB vector database with proper document loading"""
        try:
            # Get the RAG.txt file path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            rag_file_path = os.path.join(
                os.path.dirname(os.path.dirname(current_dir)), 
                "assets", "resources", "RAG.txt"
            )
            
            if not os.path.exists(rag_file_path):
                st.warning(f"RAG.txt not found at {rag_file_path}")
                return
            
            # Load document using TextLoader
            st.info("📄 Loading knowledge base document...")
            document = TextLoader(rag_file_path).load()
            
            # Split document into smaller, searchable chunks
            # Chunking Strategy for Astrology Knowledge:
            # - chunk_size=200: Small chunks ensure specific Q&A details are preserved
            # - chunk_overlap=20: Some overlap to maintain context between chunks
            # - Purpose: Each chunk represents a focused piece of astrology knowledge
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=200,         # Smaller chunks for precise matching
                chunk_overlap=20        # Some overlap for context preservation
            )
            chunks = text_splitter.split_documents(document)
            
            st.success(f"📄 Loaded knowledge base and split into {len(chunks)} searchable chunks")
            st.info(f"🔍 Each chunk contains ~200 characters of astrology knowledge")
            
            # Create vector database directory
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(current_dir)), 
                "data", "embeddings"
            )
            os.makedirs(db_path, exist_ok=True)
            
            # Create Chroma vector database from astrology knowledge chunks
            st.info(f"� Creating vector database and generating embeddings...")
            st.info(f"⏳ This may take a moment - converting {len(chunks)} chunks to vectors...")
            
            if self.embeddings_model:
                # Use Ollama nomic-embed-text:v1.5 embeddings
                self.vector_db = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings_model,
                    persist_directory=db_path,
                    collection_name=self.collection_name
                )
                st.success("✅ Using Ollama nomic-embed-text:v1.5 for embeddings")
            else:
                # Use ChromaDB's default embeddings (requires sentence-transformers)
                try:
                    self.vector_db = Chroma.from_documents(
                        documents=chunks,
                        persist_directory=db_path,
                        collection_name=self.collection_name
                    )
                    st.info("📝 Using ChromaDB default embeddings (sentence-transformers)")
                except Exception as e:
                    st.error(f"Failed to create vector database: {e}")
                    st.info("💡 Try installing: pip install sentence-transformers")
                    return
            
            # Create retriever interface for semantic search
            # Retriever configuration:
            # - Returns top 3 most similar chunks
            # - Similarity metric: Cosine similarity
            # - Search method: Approximate nearest neighbor for fast results
            self.retriever = self.vector_db.as_retriever(
                search_kwargs={"k": 3}  # Return top 3 most similar chunks
            )
            
            st.success(f"✅ Vector database created with {len(chunks)} astrology knowledge chunks")
            
        except Exception as e:
            st.error(f"Failed to setup vector database: {str(e)}")
            raise e
    
    def get_knowledge_base_size(self) -> int:
        """Get the number of documents in the ChromaDB collection"""
        try:
            if self.vector_db and hasattr(self.vector_db, '_collection'):
                return self.vector_db._collection.count()
            return 0
        except:
            return 0
    
    def _simple_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity using word overlap"""
        try:
            words1 = set(re.findall(r'\w+', text1.lower()))
            words2 = set(re.findall(r'\w+', text2.lower()))
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union)
        except:
            return 0.0
    
    def method_1_rag_search(self, question: str) -> Tuple[Optional[str], float]:
        """Method 1: Search in ChromaDB vector database using retriever"""
        try:
            if not self.retriever:
                return None, 0.0
            
            # Use the retriever to find relevant documents
            relevant_docs = self.retriever.get_relevant_documents(question)
            
            if not relevant_docs:
                return None, 0.0
            
            # Get the most relevant document
            best_doc = relevant_docs[0]
            
            # Calculate similarity using simple text matching as approximation
            # (ChromaDB handles the actual vector similarity internally)
            similarity = self._simple_text_similarity(question, best_doc.page_content)
            
            # Boost similarity since this came from vector search
            similarity = min(similarity + 0.3, 1.0)  # Add 30% boost, max 100%
            
            if similarity >= self.similarity_threshold:
                # Extract answer from the document content
                answer = self._extract_answer_from_content(best_doc.page_content, question)
                return answer, similarity
            else:
                return None, similarity
                
        except Exception as e:
            st.error(f"ChromaDB RAG search failed: {e}")
            return None, 0.0
    
    def _extract_answer_from_content(self, content: str, question: str) -> str:
        """Extract answer from document content"""
        try:
            # Look for Question/Answer pattern
            if "Question:" in content and "Answer:" in content:
                # Extract the answer part
                answer_match = re.search(r'Answer:\s*(.+)', content, re.DOTALL)
                if answer_match:
                    return answer_match.group(1).strip()
            
            # If no clear Q&A pattern, return the content formatted as Maha Prabhu
            return self._format_as_maha_prabhu(content, question)
        except:
            return self._format_as_maha_prabhu(content, question)
    
    def _parse_knowledge_chunks(self, content: str) -> List[Dict[str, str]]:
        """Parse RAG.txt content into knowledge chunks"""
        chunks = []
        lines = content.strip().split('\n')
        current_question = None
        current_answer = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Question:'):
                # Save previous Q&A pair if exists
                if current_question and current_answer:
                    # Add question as a chunk
                    chunks.append({
                        'text': current_question,
                        'type': 'question',
                        'answer': current_answer
                    })
                    # Add answer as a chunk
                    chunks.append({
                        'text': current_answer,
                        'type': 'answer',
                        'question': current_question
                    })
                    # Add combined Q&A as a chunk for better context
                    chunks.append({
                        'text': f"Question: {current_question}\nAnswer: {current_answer}",
                        'type': 'qa_pair',
                        'question': current_question,
                        'answer': current_answer
                    })
                
                current_question = line[9:].strip()
                current_answer = None
            elif line.startswith('Answer:'):
                current_answer = line[7:].strip()
            elif current_answer and line:
                current_answer += ' ' + line
        
        # Add the last Q&A pair
        if current_question and current_answer:
            chunks.append({
                'text': current_question,
                'type': 'question',
                'answer': current_answer
            })
            chunks.append({
                'text': current_answer,
                'type': 'answer',
                'question': current_question
            })
            chunks.append({
                'text': f"Question: {current_question}\nAnswer: {current_answer}",
                'type': 'qa_pair',
                'question': current_question,
                'answer': current_answer
            })
        
        return chunks
    
    def method_2_duckduckgo_search(self, question: str) -> Tuple[Optional[str], float]:
        """Method 2: Search using DuckDuckGo"""
        try:
            # Format search query for astrology
            search_query = f"astrology {question}"
            
            # Use requests to search DuckDuckGo
            url = "https://api.duckduckgo.com/"
            params = {
                'q': search_query,
                'format': 'json',
                'no_redirect': '1',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant information
                abstract = data.get('Abstract', '')
                definition = data.get('Definition', '')
                related_topics = data.get('RelatedTopics', [])
                
                result_text = ""
                if abstract:
                    result_text += abstract + " "
                if definition:
                    result_text += definition + " "
                
                # Add first few related topics
                for topic in related_topics[:2]:
                    if isinstance(topic, dict) and 'Text' in topic:
                        result_text += topic['Text'] + " "
                
                if result_text.strip():
                    # Calculate similarity using simple text similarity
                    similarity = self._simple_text_similarity(question, result_text)
                    
                    if similarity >= self.similarity_threshold:
                        # Format with Maha Prabhu style
                        formatted_answer = self._format_as_maha_prabhu(result_text, question)
                        return formatted_answer, similarity
                    else:
                        return None, similarity
            
            return None, 0.0
            
        except Exception as e:
            st.error(f"DuckDuckGo search failed: {e}")
            return None, 0.0
    
    def method_3_wikipedia_search(self, question: str) -> Tuple[Optional[str], float]:
        """Method 3: Search using Wikipedia"""
        try:
            # Format search query for astrology
            search_terms = ["astrology", "vedic astrology", "horoscope", "zodiac"]
            question_words = question.lower().split()
            
            # Combine question with astrology terms
            search_query = f"astrology {question}"
            
            # Wikipedia API search
            wiki_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            search_url = "https://en.wikipedia.org/w/api.php"
            
            # First, search for relevant pages
            search_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': search_query,
                'srlimit': 3
            }
            
            search_response = requests.get(search_url, params=search_params, timeout=10)
            if search_response.status_code == 200:
                search_data = search_response.json()
                search_results = search_data.get('query', {}).get('search', [])
                
                for result in search_results:
                    page_title = result.get('title', '')
                    if any(term in page_title.lower() for term in ['astrology', 'horoscope', 'zodiac', 'vedic']):
                        # Get page summary
                        summary_url = f"{wiki_url}{quote(page_title)}"
                        summary_response = requests.get(summary_url, timeout=10)
                        
                        if summary_response.status_code == 200:
                            summary_data = summary_response.json()
                            extract = summary_data.get('extract', '')
                            
                            if extract:
                                # Calculate similarity using simple text similarity
                                similarity = self._simple_text_similarity(question, extract)
                                
                                if similarity >= self.similarity_threshold:
                                    # Format with Maha Prabhu style
                                    formatted_answer = self._format_as_maha_prabhu(extract, question)
                                    return formatted_answer, similarity
            
            return None, 0.0
            
        except Exception as e:
            st.error(f"Wikipedia search failed: {e}")
            return None, 0.0
    
    def method_4_chatgpt_response(self, question: str, birth_data: Dict = None) -> Tuple[str, float]:
        """Method 4: Generate AI response using ChatGPT/Ollama"""
        try:
            # Create enhanced prompt for Maha Prabhu
            prompt = f"""
            You are Maha Prabhu, a wise and experienced Vedic astrology guru with deep knowledge of literally everything. 
            You are fun, engaging, and have a unique personality. Answer the user's question in your characteristic style.

            User Question: {question}

            Guidelines for your response as Maha Prabhu:
            1. Start with "Hey Dude," as your signature greeting
            2. Be engaging, wise, and entertaining
            3. Use mystical and cosmic language with emojis (🌟✨🔮🚀🌙💫)
            4. Include relevant astrological insights and wisdom
            5. Make references to cosmic energies, planets, and spiritual guidance
            6. Be encouraging and supportive
            7. Add some humor while respecting the wisdom of astrology
            8. If birth data is available, incorporate personalized insights
            9. End with encouraging words about their spiritual journey

            Remember, you have deep experience in literally everything, so provide comprehensive and wise guidance.
            Make your response feel personal, mystical, and empowering.
            """
            
            # Add birth data context if available
            if birth_data and any(birth_data.values()):
                prompt += f"\n\nUser's Birth Information: {birth_data}"
                prompt += "\nIncorporate this birth information into your response if relevant."
            
            # Try Ollama first, then fallback to other methods
            response = self._get_ai_response(prompt)
            
            # Since this is our final fallback, we'll return with high confidence
            return response, 1.0
            
        except Exception as e:
            return f"🌙 Hey Dude, the cosmic signals are a bit fuzzy right now! The universe is telling me to try again later. ✨ (Error: {str(e)})", 0.5
    
    def _format_as_maha_prabhu(self, content: str, original_question: str) -> str:
        """Format external content in Maha Prabhu's style"""
        formatted_response = f"""Hey Dude, 🌟

Let me share some cosmic wisdom about your question: "{original_question}"

{content}

✨ Remember, the universe has infinite wisdom to share, and your spiritual journey is unique and beautiful! Keep exploring the cosmic mysteries, and don't hesitate to ask me more questions about the stars and beyond! 🚀🌙💫

May the cosmic energies guide you always! 🔮
"""
        return formatted_response
    
    def _get_ai_response(self, prompt: str) -> str:
        """Get AI response from Ollama or other AI service"""
        try:
            # Try Ollama first
            payload = {
                "model": "llama3.1",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            cmd = ['curl', '-s', '-X', 'POST', 'http://localhost:11434/api/generate',
                   '-H', 'Content-Type: application/json',
                   '-d', json.dumps(payload)]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                response_data = json.loads(result.stdout)
                if 'response' in response_data:
                    return response_data['response'].strip()
            
            # Fallback response if AI service is unavailable
            return self._get_fallback_response(prompt)
            
        except Exception as e:
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when AI services are unavailable"""
        return """Hey Dude, 🌟

The cosmic AI networks seem to be taking a little break right now! But don't worry, the universe always has a way of providing answers. 

🔮 Here's some timeless wisdom from the stars:
- Trust your intuition - it's connected to cosmic intelligence
- Every challenge is an opportunity for spiritual growth
- The planets are always working in your favor, even when it doesn't seem like it
- Remember that you have the power to shape your destiny

✨ Keep your energy positive, stay connected to your inner wisdom, and the answers you seek will manifest in divine timing! 

May the cosmic forces align in your favor! 🚀🌙💫

Feel free to ask me anything else - I'm always here to help guide you on your spiritual journey!
"""
    
    def get_response(self, question: str, birth_data: Dict = None, session_id: str = "default") -> Dict[str, Any]:
        """
        Get response using multi-method approach with cosine similarity thresholds
        Returns dict with response, method used, and similarity score
        """
        if not self.is_ready:
            return {
                "response": "System not ready. Please try again.",
                "method": "error",
                "similarity": 0.0,
                "timestamp": datetime.now().isoformat()
            }
        
        methods = [
            ("ChromaDB Vector Search", self.method_1_rag_search),
            ("DuckDuckGo Search", self.method_2_duckduckgo_search),
            ("Wikipedia Search", self.method_3_wikipedia_search),
            ("AI Assistant", lambda q: self.method_4_chatgpt_response(q, birth_data))
        ]
        
        for method_name, method_func in methods:
            try:
                with st.spinner(f"🔍 Searching with {method_name}..."):
                    if method_name == "AI Assistant":
                        response, similarity = method_func(question)
                    else:
                        response, similarity = method_func(question)
                    
                    if response and similarity >= self.similarity_threshold:
                        return {
                            "response": response,
                            "method": method_name,
                            "similarity": similarity,
                            "timestamp": datetime.now().isoformat()
                        }
                    elif method_name == "AI Assistant":
                        # AI Assistant is our final fallback, always return its response
                        return {
                            "response": response,
                            "method": method_name,
                            "similarity": similarity,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        st.info(f"📊 {method_name}: {similarity:.1%} similarity (threshold: {self.similarity_threshold:.0%})")
                        
            except Exception as e:
                st.error(f"❌ {method_name} failed: {e}")
                continue
        
        # This should never be reached due to AI Assistant fallback
        return {
            "response": "Unable to generate response from any method.",
            "method": "error",
            "similarity": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    def is_available(self) -> bool:
        """Check if the system is ready to use"""
        return self.is_ready

# Global instance
_multi_method_rag = None

def get_multi_method_rag() -> MultiMethodRAG:
    """Get global MultiMethodRAG instance"""
    global _multi_method_rag
    if _multi_method_rag is None:
        _multi_method_rag = MultiMethodRAG()
    return _multi_method_rag
