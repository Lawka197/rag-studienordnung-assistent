# Projektstruktur

---
## Aktueller Stand der Ordnerstruktur

```
rag_studienordnung_assistent/
├── src/rag_studienordnung_assistent/
│   ├── chunking/              # Text-Preprocessing & Splitting
│   │   ├── chunker.py         # Main chunking orchestrator
│   │   ├── patterns.py        # Regex patterns (zentral)
│   │   ├── strategies.py      # Splitting strategies
│   │   └── chunking_config.py # Konfiguration
│   │
│   ├── embeddings/            # Embedding-Generation
│   │   └── embedder.py        # sentence-transformers wrapper
│   │
│   ├── retrieval/             # Vector Search
│   │   ├── faiss_store.py     # FAISS Vector Store
│   │   └── retriever.py       # Search orchestrator
│   │
│   ├── ingestion/             # Datenladung
│   │   └── pdf_loader.py      # PDF extraction
│   │
│   ├── llm.py                 # Ollama LLM Integration
│   ├── rag_system.py          # Main RAG System
│   ├── demo.py                # Interactive Demo
│   └── main.py                # Batch Processing
│
├── tests/                     # Test Suite (51 tests)
│   ├── test_chunking.py
│   └── test_preprocessing.py
│
├── docs/                      # Dokumentation
│   ├── evaluation_extraktion.md
│   ├── kurzbericht_rag.md
│   └── ... (weitere Docs)
│
├── data/
│   ├── raw/                   # PDF-Dateien
│   └── processed/
│       ├── chunks/            # Chunks
│       └── vector_store/      # FAISS Index
│
└── requirements.txt           # Dependencies
```
---

## Architektur

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│  (Frage: "Was ist ein Modul?")                          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              RAG-SYSTEM (MAIN)                          │
│  - load_document()  - answer_question()                 │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
┌───────▼──────┐ ┌──▼────────┐ ┌─▼─────────┐ ┌▼────────┐
│  CHUNKING    │ │ EMBEDDINGS│ │RETRIEVAL  │ │  LLM    │
│ - Preprocess │ │ - Embedder│ │- FAISS    │ │-Ollama  │
│ - Split      │ │ - Batch   │ │- Retriever│ │-Generate│
│ - Strategy   │ │ - Vectors │ │- Top-K    │ │-Answer  │
└──────────────┘ └───────────┘ └───────────┘ └─────────┘
        │            │            │            │
        └────────────┼────────────┴────────────┘
                     │
        ┌────────────▼────────────┐
        │   DATA LAYER            │
        │ - PDFs (raw/)           │
        │ - Chunks (processed/)   │
        │ - Vector Store (FAISS)  │
        └─────────────────────────┘
```