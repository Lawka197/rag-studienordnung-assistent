from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class Retriever:

    def __init__(self, vector_store, embedder):
        self.vector_store = vector_store
        self.embedder = embedder
        logger.info(f"Initialized Retriever with {len(vector_store)} chunks")


    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, float, dict]]:
        logger.debug(f"Embedding query: '{query[:50]}...'")
        query_embedding = self.embedder.embed(query)

        logger.debug(f"Searching in vector store for top {top_k} matches")
        results = self.vector_store.search(query_embedding, top_k=top_k)

        print("\n--- Retrieval Scores ---")
        for i, (text, score, metadata) in enumerate(results, 1):
            print(f"{i}. Score: {score:.3f} | Source: {metadata.get('source', 'Unknown')}")

        if results:
            avg_score = sum(score for _, score, _ in results) / len(results)
            print(f"Average score: {avg_score:.3f}")
            print("-----------------------\n")
        logger.info(f"Retrieved {len(results)} results for query")

        return results

    def retrieve_with_context(self, query: str, top_k: int = 5) -> str:
        results = self.retrieve(query, top_k=top_k)

        if not results:
            return "Keine relevanten Dokumente gefunden."

        context_parts = []
        for i, (text, score, metadata) in enumerate(results, 1):
            source = metadata.get("source", "Unknown")
            context_parts.append(
                f"[Dokument {i}] (Relevanz: {score:.2f}) - {source}\n"
                f"{text}\n"
            )

        return "\n".join(context_parts)

