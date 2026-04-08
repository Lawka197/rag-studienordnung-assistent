# RAG-System für Studienordnungen 

### Projektziel
Dieses projekt entwickelt ein RAG-basiertes Frage-Antwort-System, das Studentinnen der alten &amp; neuen Studienordnung hilft, schnelle verlässliche Informationen zu Modulen &amp; Praktikumsanforderungen zu finden.

---
### Problemstellung

Studentinnen der alten &amp; neuen Studienordnung haben Schwierigkeiten, relevante Informationen zu Modulen &amp; Praktikumsanforderungen schnell &amp; zuverlässig zu finden. Die Dokumente sind umfangreich &amp; komplex, was die Informationssuche erschwert.

**Lösung:** Ein RAG-System mit semantischer Suche und LLM-Antworten

---
### Funktionen
- Fragen zu Modulen &amp; Praktikumsanforderungen beantworten
- Unterschiede zwischen alter &amp; neuer Studienordnung aufzeigen
- Quellen und Referenzen nennen
- Praktikumsanforderungen aus offiziellen Dokumenten extrahieren


## Tech-Stack

| Komponente | Technologie | Grund |
|-----------|-----------|-------|
| **Embedding** | sentence-transformers (all-MiniLM-L6-v2) | Schnell, klein, präzise |
| **Vector Store** | FAISS | Persistent, effizient, skalierbar |
| **LLM** | Ollama (lokal) | Kostenlos, datenschutz, offline |
| **PDF Processing** | PyPDF | Robust, einfach |
| **Framework** | Python 3.11+ | Flexibel, datascience-friendly |
| **Testing** | Pytest | 51 Tests, 100% coverage |


## Projektstruktur
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

## Installation

#### **Voraussetzungen**
- Python 3.9+
- pip
- (Optional) Ollama für LLM (kostenlos)

### **Schritt 1: Repository klonen**
```bash
git clone https://github.com/olivialawinski/RAG-Studienordnung.git
cd rag_studienordnung_assistent
```

### **Schritt 2: Virtual Environment erstellen**
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# oder: .venv\Scripts\activate  # Windows
```

### **Schritt 3: Dependencies installieren**
```bash
pip install -r requirements.txt
```

### **Schritt 4: Ollama installieren (optional aber empfohlen)**
```bash
# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh

# Windows/Andere
Siehe: https://ollama.ai
```

### **Schritt 5: Ollama-Modell laden**
```bash
ollama pull neural-chat
# oder: ollama pull mistral (bessere Qualität, langsamer)
```

### **Schritt 6: Ollama starten**
```bash
ollama serve
```

---

## Konfiguration

### **Chunking-Strategien**
```python
from rag_studienordnung_assistent.chunking.chunking_config import get_config

# Standard-Konfiguration
config = get_config("default")

# Aggressive (besseres Retrieval)
config = get_config("aggressive")

# Conservative (besserer Kontext)
config = get_config("conservative")
```

### **LLM-Modelle**
```python
# neural-chat (schnell, Standard)
rag = RAGSystem(llm_type="ollama", model="neural-chat")

# mistral (besser, langsamer)
rag = RAGSystem(llm_type="ollama", model="mistral")

# llama2 (beste Qualität, langsam)
rag = RAGSystem(llm_type="ollama", model="llama2")
```



## Beispielanfragen
- Welche Module sind Pflichtmodule in der alten Studienordnung?
- Wie viele ECTS-Punkte muss ich für das Praktikum in der neuen Studienordnung erwerben
- Wie unterscheiden sich die Anforderungen für das Praktikum zwischen der alten und neuen Studienordnung?
- Wo finde ich Regelungen zu Modul X?


## Autorin

**Olivia**
- GitHub: https://github.com/Lawka197/rag-studienordnung-assistent.git
- Projekt: **RAG Studienordnung Assistent**

