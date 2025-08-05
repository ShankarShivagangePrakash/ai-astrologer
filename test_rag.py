#!/usr/bin/env python3
"""
Test script for the new ChromaDB-based Multi-Method RAG system with Ollama embeddings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_multi_method_rag():
    """Test the multi-method RAG system"""
    print("🧪 Testing Multi-Method RAG System with Ollama Embeddings")
    print("=" * 60)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from src.utils.multi_method_rag import get_multi_method_rag
        print("✅ Multi-method RAG imported successfully")
        
        # Initialize system
        print("\n🔧 Initializing system...")
        multi_rag = get_multi_method_rag()
        
        if multi_rag.is_available():
            print("✅ System initialized successfully")
            print(f"📚 Vector database size: {multi_rag.get_knowledge_base_size()} documents")
            print(f"🎯 Similarity threshold: {multi_rag.similarity_threshold:.0%}")
            print(f"🤖 Embeddings model: {'Ollama nomic-embed-text:v1.5' if multi_rag.embeddings_model else 'ChromaDB default'}")
            
            # Test queries
            test_questions = [
                "What is your name?",
                "How can I improve my health?",
                "Tell me about astrology"
            ]
            
            print(f"\n🔍 Testing {len(test_questions)} queries...")
            for i, question in enumerate(test_questions, 1):
                print(f"\n--- Test {i}/3 ---")
                print(f"Question: {question}")
                
                result = multi_rag.get_response(question)
                
                print(f"Method used: {result['method']}")
                print(f"Similarity: {result['similarity']:.1%}")
                print(f"Response preview: {result['response'][:150]}...")
                
                if result['similarity'] >= multi_rag.similarity_threshold:
                    print("✅ Found good match above threshold")
                else:
                    print("⚡ Using fallback method")
            
            return True
        else:
            print("❌ System failed to initialize")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_multi_method_rag()
    print("\n" + "=" * 60)
    if success:
        print("🎉 Test completed successfully!")
        print("💡 Tip: Make sure Ollama is running with 'ollama pull nomic-embed-text:v1.5'")
    else:
        print("💥 Test failed!")
    sys.exit(0 if success else 1)
