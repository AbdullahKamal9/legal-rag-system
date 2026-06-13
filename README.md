# Legal Contract Q&A — RAG System

An AI-powered legal contract assistant that answers questions about uploaded contracts using Retrieval Augmented Generation (RAG).

## What it does
- Upload any legal contract PDF
- Ask questions in plain English
- Get accurate answers with section and page references

## Tech Stack
- **LLM:** GPT-4o-mini (OpenAI)
- **Embeddings:** text-embedding-3-small (OpenAI)
- **Vector Store:** ChromaDB
- **Retrieval:** Hybrid Search (BM25 + Vector MMR)
- **Framework:** LangChain
- **Observability:** LangSmith
- **UI:** Streamlit

## Architecture
1. PDF uploaded and loaded via PyPDFLoader
2. Text split using RecursiveCharacterTextSplitter (chunk size 1000, overlap 200)
3. Chunks embedded using text-embedding-3-small
4. Embeddings stored in ChromaDB
5. User query retrieved using Hybrid Search (BM25 + MMR vector search)
6. Top chunks passed to GPT-4o-mini with legal assistant prompt
7. Answer returned with source page and section citation

## Why Hybrid Search?
- BM25 handles exact keyword matches (e.g. specific legal terms)
- Vector search handles semantic meaning (e.g. related concepts)
- Combining both gives better retrieval than either alone

## Setup

1. Clone the repo
2. Install dependencies: