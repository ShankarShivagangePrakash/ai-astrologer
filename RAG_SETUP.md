# Fun Chat RAG System Setup

## Overview
The Fun Chat now uses a history-aware RAG (Retrieval-Augmented Generation) system that:
- Uses **nomic-embed-text** for local embeddings (no API key required for embeddings)
- Searches the knowledge base from `RAG.txt` 
- Remembers conversation history
- Provides contextual responses based on previous interactions

## Prerequisites

### 1. Install Ollama
```bash
# Install Ollama (if not already installed)
# Visit https://ollama.ai or use:
brew install ollama  # for macOS
```

### 2. Install nomic-embed-text Model
```bash
ollama pull nomic-embed-text
```

### 3. Verify Installation
```bash
ollama list
# Should show nomic-embed-text in the list
```

## RAG System Features

### 🧠 Knowledge Base
- Uses `assets/resources/RAG.txt` as the knowledge source
- Contains Q&A pairs from "Maha Prabhu" - an experienced astrologer
- Automatically chunks and indexes the content

### 🔍 Smart Retrieval
- Semantic search using nomic-embed-text embeddings
- Finds relevant answers from the knowledge base
- Combines with conversational context

### 💬 History Awareness
- Remembers previous questions and answers
- Provides contextual follow-up responses
- Maintains separate chat histories per session

### 🎯 Fallback Modes
1. **Full RAG Mode**: OpenAI LLM + Local Embeddings + Knowledge Base
2. **Simple Retrieval**: Local Embeddings + Knowledge Base (no LLM)
3. **Standard AI**: Regular AI responses if RAG unavailable

## Usage

### Testing RAG Responses
Try these questions that match the knowledge base:

1. **"What is your name?"** - Should respond with "Maha Prabhu"
2. **"What is astrology?"** - Should mention "Hey Dude" innovation
3. **"How can I grow in life?"** - Should suggest catching a rocket
4. **"When will my problems be solved?"** - Should mention "Hey Dude" mantra
5. **"How do I take out stress?"** - Should suggest boycotting
6. **"How can I improve my health?"** - Should mention holy water

### Follow-up Questions
After asking any of the above, try:
- "Tell me more about that"
- "Can you explain further?"
- "What else can you tell me?"

The system should remember the context and provide relevant follow-ups.

## System Status

The Fun Chat page will show:
- **🧠 RAG Knowledge Base: Active** - Full RAG working
- **⚡ Basic AI Mode: Active** - Simple retrieval working
- **🌟 Standard AI Mode: Active** - Fallback mode

## Troubleshooting

### If embeddings fail:
- Check if Ollama is running: `ollama list`
- Verify nomic-embed-text is installed: `ollama pull nomic-embed-text`
- System will automatically use hash-based fallback embeddings

### If OpenAI API fails:
- System switches to simple retrieval mode
- Still provides knowledge base answers
- No conversational AI enhancement

### If RAG.txt is missing:
- System falls back to standard AI responses
- Check `assets/resources/RAG.txt` exists

## Architecture

```
User Question
     ↓
History-Aware Retrieval
     ↓
Semantic Search (nomic-embed-text)
     ↓
Knowledge Base Matching
     ↓
Context + History → LLM
     ↓
Fun, Enhanced Response
```

## Benefits

✅ **No API costs for embeddings** - Uses local nomic-embed-text  
✅ **Conversational memory** - Remembers chat history  
✅ **Domain-specific knowledge** - Uses curated astrology Q&A  
✅ **Graceful fallbacks** - Works even if some components fail  
✅ **Fun personality** - Maintains engaging chat experience  

## Knowledge Base Customization

To add more knowledge:
1. Edit `assets/resources/RAG.txt`
2. Add Q&A pairs in format:
   ```
   Question: Your question here?
   Answer: Your answer here.
   ```
3. Restart the app to reload the knowledge base

The system will automatically:
- Chunk the new content
- Generate embeddings
- Make it searchable in chat
