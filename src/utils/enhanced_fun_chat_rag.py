"""
Enhanced Fun Chat RAG with structured search approach
1. First: Search RAG embeddings from RAG.txt
2. Then: Use external tools (Wikipedia) 
3. Finally: Apply Maha Prabhu template response
"""

import os
import re
import streamlit as st
import json
import subprocess
import requests
from typing import List, Dict, Tuple, Any
from urllib.parse import quote

# Import LangChain for structured approach
try:
    from langchain_openai import ChatOpenAI
    from langchain.agents import create_react_agent, AgentExecutor
    from langchain.tools import Tool
    from langchain_community.tools import WikipediaQueryRun
    from langchain_community.utilities import WikipediaAPIWrapper
    from langchain.prompts import PromptTemplate
    from langchain.schema import OutputParserException
    LANGCHAIN_AVAILABLE = True
    st.success("🔗 LangChain libraries loaded successfully")
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    st.error(f"❌ LangChain import failed: {e}")
    st.info("💡 Install with: pip install langchain langchain-openai langchain-community wikipedia")

class EnhancedFunChatRAG:
    def __init__(self):
        self.knowledge_base = {}
        self.questions = []
        self.answers = []
        self.question_embeddings = []
        self.is_ready = False
        self.agent_executor = None
        self.use_langchain = False
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the structured RAG system"""
        try:
            # Always load knowledge base first
            self._load_knowledge_base()
            
            # Setup LangChain agent if available
            if LANGCHAIN_AVAILABLE:
                if os.getenv("OPENAI_API_KEY"):
                    self._setup_structured_agent()
                    self.use_langchain = True
                    st.success("🤖 Structured Agent Mode: RAG → External Tools → Maha Prabhu Response")
                else:
                    st.warning("⚠️ OPENAI_API_KEY not found. Please set it for LangChain agent.")
                    self.use_langchain = False
            else:
                st.error("❌ LangChain not available. Please install required dependencies.")
                self.use_langchain = False
            
            self.is_ready = True
            
        except Exception as e:
            st.error(f"Failed to initialize Enhanced Fun Chat RAG: {e}")
            self.is_ready = False
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using nomic-embed-text"""
        try:
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
            
            return self._hash_embedding(text)
            
        except Exception as e:
            return self._hash_embedding(text)
    
    def _hash_embedding(self, text: str) -> List[float]:
        """Create a simple hash-based embedding as fallback"""
        import hashlib
        
        words = re.findall(r'\w+', text.lower())
        embedding = [0.0] * 768
        
        for word in words:
            word_hash = hashlib.sha256(word.encode()).digest()
            for i in range(0, len(word_hash), 4):
                if i + 3 < len(word_hash):
                    pos = int.from_bytes(word_hash[i:i+4], 'big') % 768
                    embedding[pos] += 1.0
        
        # Normalize
        norm = sum(x * x for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def _load_knowledge_base(self):
        """Load RAG.txt and create embeddings"""
        try:
            rag_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "assets", "resources", "RAG.txt"
            )
            
            if not os.path.exists(rag_file_path):
                st.warning(f"RAG.txt not found at {rag_file_path}")
                return
            
            with open(rag_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            qa_pairs = self._parse_qa_pairs(content)
            
            if qa_pairs:
                self.knowledge_base = qa_pairs
                self.questions = list(qa_pairs.keys())
                self.answers = list(qa_pairs.values())
                
                # Generate embeddings for all questions
                self.question_embeddings = []
                for question in self.questions:
                    embedding = self._get_embedding(question)
                    self.question_embeddings.append(embedding)
                
                st.success(f"📚 Enhanced RAG ready with {len(qa_pairs)} Q&A pairs and embeddings")
            else:
                st.warning("No Q&A pairs found in RAG.txt")
                
        except Exception as e:
            st.error(f"Failed to load knowledge base: {str(e)}")
    
    def _parse_qa_pairs(self, content: str) -> Dict[str, str]:
        """Parse Q&A pairs from RAG.txt content"""
        qa_pairs = {}
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
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            min_len = min(len(vec1), len(vec2))
            vec1 = vec1[:min_len]
            vec2 = vec2[:min_len]
            
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            mag1 = sum(a * a for a in vec1) ** 0.5
            mag2 = sum(b * b for b in vec2) ** 0.5
            
            if mag1 == 0 or mag2 == 0:
                return 0.0
            
            return dot_product / (mag1 * mag2)
        except Exception:
            return 0.0
    
    def _search_rag_knowledge(self, question: str) -> Dict[str, Any]:
        """Search RAG knowledge base using embeddings"""
        if not self.knowledge_base or not self.question_embeddings:
            return {"found": False, "similarity": 0.0, "answer": "", "matched_question": ""}
        
        try:
            # Check exact match first
            user_q_lower = question.lower().strip()
            if user_q_lower in self.knowledge_base:
                return {
                    "found": True,
                    "similarity": 1.0,
                    "answer": self.knowledge_base[user_q_lower],
                    "matched_question": user_q_lower
                }
            
            # Use embedding similarity
            user_embedding = self._get_embedding(question)
            best_score = 0.0
            best_answer = ""
            best_question = ""
            
            for i, kb_embedding in enumerate(self.question_embeddings):
                similarity = self._cosine_similarity(user_embedding, kb_embedding)
                if similarity > best_score:
                    best_score = similarity
                    best_answer = self.answers[i]
                    best_question = self.questions[i]
            
            return {
                "found": best_score > 0.65,  # Increased threshold to 65% for better precision
                "similarity": best_score,
                "answer": best_answer,
                "matched_question": best_question
            }
            
        except Exception as e:
            return {"found": False, "similarity": 0.0, "answer": "", "matched_question": "", "error": str(e)}
    
    def _setup_structured_agent(self):
        """Setup structured LangChain agent with proper search flow"""
        try:
            # Initialize OpenAI
            llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
            
            # Tool 1: RAG Knowledge Search
            def rag_search_tool(query: str) -> str:
                """STEP 1: Search Maha Prabhu's RAG embeddings from RAG.txt"""
                result = self._search_rag_knowledge(query)
                if result["found"]:
                    similarity_percent = int(result["similarity"] * 100)
                    return f"✅ RAG FOUND ({similarity_percent}% match): {result['answer']}"
                else:
                    similarity_percent = int(result["similarity"] * 100)
                    return f"❌ RAG NOT FOUND (best match: {similarity_percent}%) - Need external search"
            
            # Tool 2: Wikipedia Search
            def wikipedia_search_tool(query: str) -> str:
                """STEP 2a: Search Wikipedia for external knowledge"""
                try:
                    search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(query)}"
                    response = requests.get(search_url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        extract = data.get('extract', 'No information found')
                        if extract and len(extract) > 10:
                            return f"📖 WIKIPEDIA FOUND: {extract[:500]}..."
                    return "❌ Wikipedia: No information found"
                except Exception as e:
                    return f"❌ Wikipedia error: {e}"
            
            # Create structured tools
            tools = [
                Tool(
                    name="search_rag_embeddings",
                    func=rag_search_tool,
                    description="ALWAYS use this FIRST to search RAG embeddings from RAG.txt knowledge base"
                ),
                Tool(
                    name="search_wikipedia", 
                    func=wikipedia_search_tool,
                    description="Use this SECOND if RAG search fails - search Wikipedia for factual information"
                )
            ]
            
            # Create structured prompt template
            prompt_template = """You are Maha Prabhu, a mystical astrology guru with cosmic wisdom and a "Hey Dude" personality.

STRUCTURED SEARCH PROCESS:
1. ALWAYS search RAG embeddings FIRST using search_rag_embeddings
2. If RAG fails, search Wikipedia using search_wikipedia  
3. Apply Maha Prabhu template to the results

Question: {input}

Thought: I need to follow the structured search process. First, let me search my RAG embeddings.

Action: search_rag_embeddings
Action Input: {input}
Observation: {agent_scratchpad}

Thought: Based on the RAG result, I need to decide next steps. If RAG found answer, I'll use it. If not, I'll search external tools.

Action: [Use search_wikipedia if RAG failed, otherwise skip to Final Answer]
Action Input: {input}
Observation: [Wikipedia results if used]

Thought: [Evaluate Wikipedia results, proceed to Final Answer with best available information]

Final Answer: Hey Dude! [Respond based on best available information in Maha Prabhu's mystical style with cosmic emojis and direct guidance]

Available tools: {tools}
Tool names: {tool_names}

{agent_scratchpad}"""
            
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["input", "agent_scratchpad"],
                partial_variables={
                    "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
                    "tool_names": ", ".join([tool.name for tool in tools])
                }
            )
            
            # Create structured agent
            agent = create_react_agent(llm, tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=6,  # Allow enough iterations for 3-step search
                return_intermediate_steps=True
            )
            
            st.success("🎯 Structured Agent Ready: RAG → Wikipedia → Maha Prabhu")
            
        except Exception as e:
            st.error(f"❌ Could not setup structured agent: {e}")
            self.use_langchain = False
    
    def _search_wikipedia_direct(self, query: str) -> str:
        """Direct Wikipedia search without LangChain"""
        try:
            import requests
            from urllib.parse import quote
            
            # Wikipedia API search
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(query)}"
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('extract', 'No information found')
            else:
                return "Wikipedia search failed"
                
        except Exception as e:
            return f"Wikipedia search error: {e}"
    
    def _apply_maha_prabhu_template(self, question: str, rag_result: Dict[str, Any], external_info: str = "") -> str:
        """Apply the Maha Prabhu template logic to generate response"""
        
        # Step 1: Check RAG knowledge base
        if rag_result["found"]:
            # Found in RAG - use cosmic database wisdom
            return f"Hey Dude, {rag_result['answer']} ✨"
        
        # Step 2: No RAG match - use external tools if available
        elif external_info and external_info not in ["No information found", "Search failed", "No specific information found"]:
            # Found external information - blend with mystical perspective
            return f"""Hey Dude, the universal cosmic forces (via my mystical web search) have revealed: 🔮

{external_info}

🌟 Now let me channel this through Maha Prabhu's mystical lens: This earthly knowledge connects to the cosmic dance of planets and stars! Each piece of information in the universe resonates with astrological wisdom. 

Consider how this knowledge might align with your birth chart and cosmic journey! The stars whisper that understanding leads to enlightenment! ✨

🚀 Want me to dive deeper into the mystical aspects? Ask away! 🌙"""
        
        # Step 3: No good information found anywhere
        else:
            best_similarity = int(rag_result.get("similarity", 0) * 100)
            return f"""Hey Dude, even my cosmic embeddings and universal tools are working hard on this one! 🌙

My cosmic database shows {best_similarity}% similarity to existing wisdom, but not quite enough to unlock the full mystical answer. Sometimes the universe keeps its deeper secrets! ✨

🔮 The planets are always moving, and so are we on our spiritual journey. Every question you ask brings you closer to cosmic understanding! Feel free to rephrase your question or ask something else! 🌟"""
    
    def get_response(self, question: str, birth_data=None, session_id="default") -> str:
        """Get structured response: RAG → External Tools → Maha Prabhu Template"""
        if not self.is_ready:
            return self._fallback_response(question)
        
        try:
            if self.use_langchain and self.agent_executor and LANGCHAIN_AVAILABLE:
                # Use structured LangChain agent
                st.info("🎯 Using Structured Agent: RAG → Wikipedia → Response")
                
                result = self.agent_executor.invoke({"input": question})
                
                # Get the final answer
                if isinstance(result, dict) and "output" in result:
                    return result["output"]
                else:
                    # Fallback if agent fails
                    return self._structured_fallback_search(question)
                    
            else:
                # LangChain not available - use manual structured search
                st.warning("⚠️ LangChain not available. Install dependencies for full structured agent.")
                return self._structured_fallback_search(question)
                
        except Exception as e:
            st.error(f"❌ Structured search error: {str(e)}")
            return self._structured_fallback_search(question)
    
    def _structured_fallback_search(self, question: str) -> str:
        """Manual structured search when LangChain fails"""
        # Step 1: Search RAG embeddings first
        rag_result = self._search_rag_knowledge(question)
        
        if rag_result["found"]:
            # Found in RAG - return immediately
            return f"Hey Dude, {rag_result['answer']} ✨"
        
        # Step 2: RAG failed - try Wikipedia
        try:
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(question)}"
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                wiki_info = data.get('extract', '')
                
                if wiki_info and len(wiki_info) > 10:
                    return f"""Hey Dude, the universal cosmic forces (via Wikipedia) have revealed: 🔮

{wiki_info}

🌟 Now let me channel this through Maha Prabhu's mystical lens: This earthly knowledge connects to the cosmic dance of planets and stars! Every piece of universal information resonates with astrological wisdom.

Consider how this knowledge aligns with your spiritual journey! The cosmos teaches us through all forms of knowledge! ✨

🚀 Want me to dive deeper into the mystical aspects? Ask away! 🌙"""
        except Exception:
            pass
        
        # Step 3: All searches failed
        best_similarity = int(rag_result.get("similarity", 0) * 100)
        return f"""Hey Dude, even my cosmic embeddings and universal search tools are working hard on this one! 🌙

My cosmic database shows {best_similarity}% similarity to existing wisdom, but the universe is keeping deeper secrets for now! ✨

🔮 Remember, every question brings you closer to cosmic understanding. Sometimes the journey of seeking is more important than the immediate answer!

Feel free to rephrase your question or ask something else! The planets are always ready to share their wisdom! 🌟"""
    
    def _fallback_response(self, question: str) -> str:
        """Fallback response when all systems fail"""
        return """🌟 Hey Dude, the cosmic signals are a bit fuzzy right now! ✨ 

While I'm consulting the universal forces, the answer to your question isn't coming through clearly at the moment. 🌙 

🔮 Feel free to rephrase your question or ask something else - sometimes a different approach unlocks the cosmic wisdom! �"""
    
    def is_available(self) -> bool:
        """Check if enhanced RAG system is ready"""
        return self.is_ready and bool(self.knowledge_base)

# Global instance
_enhanced_rag = None

def get_enhanced_fun_chat_rag():
    """Get or create the enhanced RAG instance"""
    global _enhanced_rag
    if _enhanced_rag is None:
        _enhanced_rag = EnhancedFunChatRAG()
    return _enhanced_rag
