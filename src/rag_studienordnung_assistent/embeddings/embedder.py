from typing import List, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class Embedder:


    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):

        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):

        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Lade Embedding-Modell: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Modell {self.model_name} geladen")
        except ImportError:
            raise ImportError(
                "sentence-transformers nicht installiert. "
                "Installiere mit: pip install sentence-transformers"
            )

    def embed(self, text: str) -> np.ndarray:

        if self.model is None:
            raise RuntimeError("Modell nicht geladen")

        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding

    def embed_batch(self, texts: List[str]) -> np.ndarray:

        if self.model is None:
            raise RuntimeError("Modell nicht geladen")

        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings

    def get_embedding_dimension(self) -> int:

        if self.model is None:
            raise RuntimeError("Modell nicht geladen")

        dummy_embedding = self.model.encode("test", normalize_embeddings=True)
        return len(dummy_embedding)

    def __repr__(self) -> str:
        dim = self.get_embedding_dimension()
        return f"Embedder(model={self.model_name}, dim={dim})"


