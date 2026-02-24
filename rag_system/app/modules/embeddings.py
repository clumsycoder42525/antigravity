import logging
from sentence_transformers import SentenceTransformer
from ..core.config import Config

logger = logging.getLogger(__name__)

class EmbeddingProvider:
    """
    Provides embeddings using HuggingFace sentence-transformers.
    """
    def __init__(self, model_name: str = Config.EMBEDDING_MODEL_NAME):
        logger.info(f"Initializing embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts).tolist()

    def generate_query_embedding(self, text: str) -> list[float]:
        return self.model.encode(text).tolist()
