from sentence_transformers import SentenceTransformer
from ..config.settings import settings
import logging

logger = logging.getLogger(__name__)


class Embedder:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Embedder, cls).__new__(cls)
            logger.info(f"Loading embedding model: {settings.embedding_model_name}")
            cls._model = SentenceTransformer(settings.embedding_model_name)
        return cls._instance

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string."""
        return self._model.encode(text).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents."""
        return self._model.encode(texts).tolist()
