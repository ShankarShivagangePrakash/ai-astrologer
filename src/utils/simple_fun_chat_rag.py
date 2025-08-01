"""
RAG implementation for Fun Chat using nomic-embed-text embeddings
Uses Ollama's nomic-embed-text model for semantic similarity
"""

import os
import re
import streamlit as st
import numpy as np
from typing import List, Dict, Tuple
import json
import subprocess

class SimpleFunChatRAG:
    def __init__(self):
        self.knowledge_base = {}
        self.questions = []
        self.answers = []
        self.question_embeddings = []
        self.is_ready = False
        self._check_ollama_available()
        self._load_knowledge_base()
    
    def _check_ollama_available(self):
        """Check if ollama and nomic-embed-text are available"""
        try:
            # Check if ollama is installed and running
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                st.warning("⚠️ Ollama is not running. Using fallback text matching.")
                return False
            
            # Check if nomic-embed-text model is available
            if 'nomic-embed-text' not in result.stdout:
                st.warning("⚠️ nomic-embed-text model not found. Please run: `ollama pull nomic-embed-text`")
                return False
            
            st.success("✅ Ollama and nomic-embed-text are available")
            return True
            
        except subprocess.TimeoutExpired:
            st.warning("⚠️ Ollama timeout. Using fallback text matching.")
            return False
        except FileNotFoundError:
            st.warning("⚠️ Ollama not installed. Using fallback text matching.")
            return False
        except Exception as e:
            st.warning(f"⚠️ Ollama check failed: {e}. Using fallback text matching.")
            return False
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text using nomic-embed-text"""
        try:
            # Use ollama embeddings API
            payload = {
                "model": "nomic-embed-text",
                "prompt": text
            }
            
            cmd = ['curl', '-s', '-X', 'POST', 'http://localhost:11434/api/embeddings',
                   '-H', 'Content-Type: application/json',
                   '-d', json.dumps(payload)]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                response_data = json.loads(result.stdout)
                if 'embedding' in response_data:
                    return response_data['embedding']
            
            # Fallback to simple hash-based embedding
            return self._hash_embedding(text)
            
        except Exception as e:
            st.warning(f"Embedding error for '{text[:20]}...': {e}")
            return self._hash_embedding(text)
    
    def _hash_embedding(self, text: str) -> List[float]:
        """Create a simple hash-based embedding as fallback"""
        import hashlib
        
        # Create a more sophisticated hash embedding
        words = re.findall(r'\w+', text.lower())
        
        # Create a 768-dimensional embedding (same as nomic-embed-text)
        embedding = [0.0] * 768
        
        for word in words:
            # Use word hash to determine positions in embedding
            word_hash = hashlib.sha256(word.encode()).digest()
            for i in range(0, len(word_hash), 4):
                if i + 3 < len(word_hash):
                    # Convert 4 bytes to an index
                    pos = int.from_bytes(word_hash[i:i+4], 'big') % 768
                    embedding[pos] += 1.0
        
        # Normalize
        norm = sum(x * x for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def _load_knowledge_base(self):
        """Load RAG.txt and parse Q&A pairs with embeddings"""
        try:
            # Load RAG.txt from assets/resources
            rag_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "assets", "resources", "RAG.txt"
            )
            
            if not os.path.exists(rag_file_path):
                st.warning(f"RAG.txt not found at {rag_file_path}")
                return
            
            with open(rag_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse Q&A pairs
            qa_pairs = self._parse_qa_pairs(content)
            
            if qa_pairs:
                self.knowledge_base = qa_pairs
                
                # Create embeddings for all questions
                with st.spinner("🧮 Creating embeddings for knowledge base..."):
                    self.questions = list(qa_pairs.keys())
                    self.answers = list(qa_pairs.values())
                    
                    # Generate embeddings for all questions
                    self.question_embeddings = []
                    for question in self.questions:
                        embedding = self._get_embedding(question)
                        self.question_embeddings.append(embedding)
                
                self.is_ready = True
                st.success(f"📚 Knowledge base ready with {len(qa_pairs)} Q&A pairs and semantic embeddings")
            else:
                st.warning("No Q&A pairs found in RAG.txt")
                
        except Exception as e:
            st.error(f"Failed to load knowledge base: {str(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
    
    def _parse_qa_pairs(self, content: str) -> Dict[str, str]:
        """Parse Q&A pairs from RAG.txt content"""
        qa_pairs = {}
        
        # Split by double newlines to separate Q&A blocks
        blocks = content.strip().split('\n\n')
        
        for block in blocks:
            if 'Question:' in block and 'Answer:' in block:
                lines = block.strip().split('\n')
                question = ""
                answer = ""
                current_section = None
                
                for line in lines:
                    if line.startswith('Question:'):
                        current_section = 'question'
                        question = line.replace('Question:', '').strip()
                    elif line.startswith('Answer:'):
                        current_section = 'answer'
                        answer = line.replace('Answer:', '').strip()
                    elif current_section == 'question':
                        question += ' ' + line.strip()
                    elif current_section == 'answer':
                        answer += ' ' + line.strip()
                
                if question and answer:
                    qa_pairs[question.lower().strip()] = answer.strip()
        
        return qa_pairs
    
    def _find_best_match(self, user_question: str) -> Tuple[str, float]:
        """Find the best matching answer using embedding similarity"""
        user_q_lower = user_question.lower().strip()
        
        # First, try exact match
        if user_q_lower in self.knowledge_base:
            return self.knowledge_base[user_q_lower], 1.0
        
        # If we have embeddings, use semantic similarity
        if self.question_embeddings and len(self.question_embeddings) == len(self.questions):
            return self._find_best_match_with_embeddings(user_question)
        
        # Fallback to simple text matching
        best_match = ""
        best_score = 0.0
        
        for kb_question, kb_answer in self.knowledge_base.items():
            # Calculate simple similarity
            score = self._calculate_text_similarity(user_q_lower, kb_question)
            
            if score > best_score:
                best_score = score
                best_match = kb_answer
        
        return best_match, best_score
    
    def _find_best_match_with_embeddings(self, user_question: str) -> Tuple[str, float]:
        """Find best match using embedding similarity"""
        try:
            # Get embedding for user question
            user_embedding = self._get_embedding(user_question)
            
            best_score = 0.0
            best_answer = ""
            
            # Calculate cosine similarity with all question embeddings
            for i, kb_embedding in enumerate(self.question_embeddings):
                similarity = self._cosine_similarity(user_embedding, kb_embedding)
                
                if similarity > best_score:
                    best_score = similarity
                    best_answer = self.answers[i]
            
            return best_answer, best_score
            
        except Exception as e:
            st.warning(f"Embedding similarity error: {e}")
            # Fallback to text similarity
            return self._find_best_match_text_only(user_question)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            # Convert to same length if needed
            min_len = min(len(vec1), len(vec2))
            vec1 = vec1[:min_len]
            vec2 = vec2[:min_len]
            
            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # Calculate magnitudes
            mag1 = sum(a * a for a in vec1) ** 0.5
            mag2 = sum(b * b for b in vec2) ** 0.5
            
            # Avoid division by zero
            if mag1 == 0 or mag2 == 0:
                return 0.0
            
            return dot_product / (mag1 * mag2)
            
        except Exception:
            return 0.0
    
    def _find_best_match_text_only(self, user_question: str) -> Tuple[str, float]:
        """Fallback to text-only matching"""
        user_q_lower = user_question.lower().strip()
        best_match = ""
        best_score = 0.0
        
        for kb_question, kb_answer in self.knowledge_base.items():
            score = self._calculate_text_similarity(user_q_lower, kb_question)
            if score > best_score:
                best_score = score
                best_match = kb_answer
        
        return best_match, best_score
    
    def _calculate_text_similarity(self, q1: str, q2: str) -> float:
        """Calculate simple word-based similarity"""
        q1_words = set(re.findall(r'\w+', q1.lower()))
        q2_words = set(re.findall(r'\w+', q2.lower()))
        
        if not q1_words or not q2_words:
            return 0.0
        
        intersection = q1_words.intersection(q2_words)
        union = q1_words.union(q2_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def get_response(self, question: str, birth_data=None, session_id="default") -> str:
        """Get response from knowledge base using embeddings"""
        if not self.is_ready or not self.knowledge_base:
            return self._fallback_response(question)
        
        try:
            # Find best matching answer
            best_answer, score = self._find_best_match(question)
            
            # Use different thresholds for embedding vs text similarity
            threshold = 0.5 if self.question_embeddings else 0.3
            
            # If we have a good match, use it
            if score > threshold and best_answer:
                # Add fun formatting to the response
                fun_response = f"🌟 {best_answer} ✨\n\n"
                
                # Add birth data context if available
                if birth_data and birth_data.get('date'):
                    location_info = birth_data.get('location', {})
                    if isinstance(location_info, dict):
                        city = location_info.get('city', '')
                        state = location_info.get('state', '')
                        country = location_info.get('country', '')
                        location_str = f"{city}, {state}, {country}" if state else f"{city}, {country}"
                    else:
                        location_str = birth_data.get('place', 'Not specified')
                    
                    fun_response += f"🎯 Considering your cosmic details: Born on {birth_data['date']} at {birth_data.get('time', 'unknown time')} in {location_str}! 🌙\n\n"
                
                fun_response += "🚀 This wisdom comes from Maha Prabhu's cosmic knowledge! Ask me more! 🔮"
                
                return fun_response
            else:
                # No good match found, use fallback
                return self._fallback_response(question)
                
        except Exception as e:
            st.error(f"RAG error: {str(e)}")
            return self._fallback_response(question)
    
    def _fallback_response(self, question: str) -> str:
        """Fallback response when no match found"""
        return """🌟 Hmm, that's an interesting cosmic question! ✨ 

While I don't have specific wisdom for that in my knowledge base, let me share some general astrology insights! 🌙 

Did you know that each zodiac sign has unique planetary rulers? For example, Mars rules Aries, Venus rules Taurus and Libra! 💫

Try asking me:
• "What is your name?"
• "What is astrology?" 
• "How can I grow in life?"
• "How do I take out stress?"

🚀 These questions unlock special wisdom from my cosmic database! 🔮"""
    
    def is_available(self) -> bool:
        """Check if RAG system is ready"""
        return self.is_ready and bool(self.knowledge_base)

# Global instance
_simple_rag = None

def get_simple_fun_chat_rag():
    """Get or create the simple RAG instance"""
    global _simple_rag
    if _simple_rag is None:
        _simple_rag = SimpleFunChatRAG()
    return _simple_rag
