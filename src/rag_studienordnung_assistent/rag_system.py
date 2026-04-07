from pathlib import Path
import logging
from rag_studienordnung_assistent.ingestion.pdf_loader import extract_text_from_pdf
from rag_studienordnung_assistent.chunking.chunker import chunk_document
from rag_studienordnung_assistent.chunking.chunking_config import get_config
from rag_studienordnung_assistent.embeddings.embedder import Embedder
from rag_studienordnung_assistent.retrieval.faiss_store import FAISSVectorStore
from rag_studienordnung_assistent.retrieval.retriever import Retriever
from rag_studienordnung_assistent.llm import OllamaLLM

logger = logging.getLogger(__name__)

class RAGSystem:

    def __init__(self, chunking_config=None, llm_type: str = "ollama", **llm_kwargs):
        self.chunking_config = chunking_config or get_config("default")
        self.embedder = Embedder()
        self.vector_store = FAISSVectorStore(
            embedding_dim=self.embedder.get_embedding_dimension()
        )
        self.retriever = Retriever(self.vector_store, self.embedder)
        try:
            self.llm = OllamaLLM(**llm_kwargs) if not llm_kwargs else OllamaLLM()
            self.llm_type = llm_type
        except Exception as e:
            logger.warning(f"LLM nicht verfügbar: {e}. Nutze nur Retrieved Chunks.")
            self.llm = None

        logger.info(f"RAG System initialized (LLM: {llm_type})")

    def load_document(self, pdf_path: Path, doc_name: str = None):
        if doc_name is None:
            doc_name = pdf_path.stem

        logger.info(f"Loading document: {pdf_path}")

        text = extract_text_from_pdf(pdf_path)
        logger.info(f"Extracted {len(text)} characters from PDF")

        doc_type = "studienordnung" if "studienordnung" in doc_name.lower() else "modulhandbuch"
        chunks = chunk_document(text, doc_type, self.chunking_config)
        logger.info(f"Created {len(chunks)} chunks")

        logger.info("Generating embeddings...")
        embeddings = self.embedder.embed_batch(chunks)

        metadatas = [
            {
                "source": doc_name,
                "chunk_id": i,
                "doc_path": str(pdf_path),
            }
            for i in range(len(chunks))
        ]

        self.vector_store.add_batch(chunks, embeddings, metadatas)
        logger.info(f"Added {len(chunks)} chunks to FAISS Vector Store")

    def retrieve_context(self, query: str, top_k: int = 5) -> str:
        logger.info(f"Retrieving context for query: '{query}'")
        context = self.retriever.retrieve_with_context(query, top_k=top_k)
        return context

    def answer_question(self, question: str, top_k: int = 5, use_llm: bool = True) -> dict:
        logger.info(f"Answering question: '{question}'")

        chunks = self.retriever.retrieve(question, top_k=top_k)
        context = self.retriever.retrieve_with_context(question, top_k=top_k)

        result = {
            "question": question,
            "context": context,
            "chunks": chunks,
            "num_chunks_retrieved": len(chunks),
        }

        if use_llm and self.llm:
            try:
                logger.info("Generating answer with LLM...")
                llm_answer = self.llm.answer_question(question, context)
                result["llm_answer"] = llm_answer
                logger.info("LLM Answer generated successfully")
            except Exception as e:
                logger.warning(f"Error generating LLM answer: {e}")
                result["llm_answer"] = f"Fehler bei LLM-Generierung: {e}"
        elif use_llm and not self.llm:
            result["llm_answer"] = "LLM nicht verfügbar. Starte Ollama mit: ollama serve"

        return result



