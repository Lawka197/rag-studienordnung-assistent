from typing import List, Tuple, Optional
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FAISSVectorStore:

    def __init__(self, embedding_dim: int = 384):
        try:
            import faiss
            self.faiss = faiss
        except ImportError:
            raise ImportError(
                "FAISS nicht installiert. "
                "Installiere mit: pip install faiss-cpu"
                "(oder faiss-gpu für GPU)"
            )

        self.embedding_dim = embedding_dim
        self.texts: List[str] = []
        self.metadata: List[dict] = []
        self.index = self.faiss.IndexFlatIP(embedding_dim)

        logger.info(f"Initialized FAISS Vector Store (dim={embedding_dim})")

    def add(self, text: str, embedding: np.ndarray, metadata: dict = None):
        embedding = np.asarray(embedding, dtype=np.float32).reshape(1, -1)

        if embedding.shape[1] != self.embedding_dim:
            raise ValueError(
                f"Falsche Embedding-Dimension: {embedding.shape[1]} statt {self.embedding_dim}"
        )

        self.faiss.normalize_L2(embedding)

        self.index.add(embedding)
        self.texts.append(text)
        self.metadata.append(metadata or {})

        logger.debug(f"Added text (length={len(text)}) to FAISS. Total: {len(self.texts)}")

    def add_batch(self, texts: List[str], embeddings: np.ndarray, metadatas: List[dict] = None):
        if metadatas is None:
            metadatas = [{} for _ in texts]

        assert len(texts) == len(embeddings) == len(metadatas), \
            "Längen müssen gleich sein"

        embeddings = embeddings.astype(np.float32)

        self.index.add(embeddings)
        self.texts.extend(texts)
        self.metadata.extend(metadatas)

        logger.info(f"Added batch of {len(texts)} texts. Total: {len(self.texts)}")

    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        if len(self.texts) == 0:
            logger.warning("Vector store ist leer!")
            return []

        query_embedding = np.asarray(query_embedding, dtype=np.float32).reshape(1, -1)

        if query_embedding.shape[1] != self.embedding_dim:
            raise ValueError(
                f"Falsche Query-Dimension: {query_embedding.shape[1]} statt {self.embedding_dim}"
            )

        self.faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(query_embedding, min(top_k, len(self.texts)))

        results = []
        for i, score in zip(indices[0], scores[0]):
            if i == -1:
                continue
            results.append((self.texts[i], float(score), self.metadata[i]))

        return results

    def save(self, path: str):
        import faiss
        import json

        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        index_path = path / "index.faiss"
        faiss.write_index(self.index, str(index_path))

        data = {
            "texts": self.texts,
            "metadata": self.metadata,
            "embedding_dim": self.embedding_dim,
        }

        data_path = path / "data.json"
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved FAISS vector store to {path}")

    @classmethod
    def load(cls, path: str) -> "FAISSVectorStore":
        import faiss
        import json

        path = Path(path)
        index_path = path / "index.faiss"
        index = faiss.read_index(str(index_path))

        data_path = path / "data.json"
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        store = cls(embedding_dim=data["embedding_dim"])
        store.index = index
        store.texts = data["texts"]
        store.metadata = data["metadata"]

        logger.info(f"Loaded FAISS vector store from {path}")
        return store

    def __len__(self) -> int:
        return len(self.texts)

    def __repr__(self) -> str:
        return f"FAISSVectorStore(size={len(self.texts)}, dim={self.embedding_dim})"



