#!/usr/bin/env python3
"""
Refresh Embeddings Script
This script clears old embeddings and regenerates them from the updated RAG.txt file.
"""

import os
import shutil
import sys
from pathlib import Path

def clear_embeddings():
    """Clear existing ChromaDB embeddings"""
    current_dir = Path(__file__).parent
    embeddings_dir = current_dir / "data" / "embeddings"
    
    print(f"🧹 Clearing embeddings directory: {embeddings_dir}")
    
    if embeddings_dir.exists():
        try:
            # Remove all files and directories in embeddings folder
            for item in embeddings_dir.iterdir():
                if item.is_file():
                    item.unlink()
                    print(f"   Deleted file: {item.name}")
                elif item.is_dir():
                    shutil.rmtree(item)
                    print(f"   Deleted directory: {item.name}")
            
            print("✅ Successfully cleared old embeddings")
            return True
        except Exception as e:
            print(f"❌ Error clearing embeddings: {e}")
            return False
    else:
        print("📁 Embeddings directory doesn't exist - nothing to clear")
        return True

def check_rag_file():
    """Check if RAG.txt file exists and show preview"""
    current_dir = Path(__file__).parent
    rag_file = current_dir / "assets" / "resources" / "RAG.txt"
    
    if not rag_file.exists():
        print(f"❌ RAG.txt not found at: {rag_file}")
        return False
    
    print(f"📄 Found RAG.txt at: {rag_file}")
    
    # Show content preview
    try:
        with open(rag_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')
            
        # Count questions
        questions = [line for line in lines if line.strip().startswith('Question:')]
        print(f"📊 RAG.txt contains {len(questions)} questions")
        
        # Show first few questions as preview
        print("\n📝 Preview of questions in RAG.txt:")
        for i, q in enumerate(questions[:3]):
            print(f"   {i+1}. {q.strip()}")
        
        if len(questions) > 3:
            print(f"   ... and {len(questions) - 3} more questions")
            
        return True
        
    except Exception as e:
        print(f"❌ Error reading RAG.txt: {e}")
        return False

def main():
    """Main function to refresh embeddings"""
    print("🚀 Refreshing ChromaDB Embeddings")
    print("=" * 50)
    
    # Step 1: Check RAG.txt file
    print("\n1️⃣ Checking RAG.txt file...")
    if not check_rag_file():
        print("❌ Cannot proceed without valid RAG.txt file")
        sys.exit(1)
    
    # Step 2: Clear old embeddings
    print("\n2️⃣ Clearing old embeddings...")
    if not clear_embeddings():
        print("❌ Failed to clear old embeddings")
        sys.exit(1)
    
    # Step 3: Instructions for regeneration
    print("\n3️⃣ Embeddings cleared successfully!")
    print("\n📋 Next steps:")
    print("   1. Start your Streamlit app: streamlit run streamlit_app.py")
    print("   2. Go to the Fun Chat page")
    print("   3. The new embeddings will be automatically generated from your updated RAG.txt")
    print("   4. This happens the first time you access the Multi-Method RAG system")
    
    print("\n✅ Embedding refresh preparation complete!")
    print("💡 The new embeddings will only include questions that are currently in your RAG.txt file")

if __name__ == "__main__":
    main()
