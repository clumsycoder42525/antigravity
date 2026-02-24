import math
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from ..rag.embedder import Embedder
from ..config.settings import settings

logger = logging.getLogger(__name__)

class EmbeddingIndexManager:
    """
    Manages semantic indexing of memory keys and ranking for recall.
    """
    def __init__(self):
        self.embedder = Embedder()
        self.cache_path = Path(settings.memory_embedding_cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache = self._load_cache()

    def _load_cache(self) -> Dict[str, List[float]]:
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load embedding cache: {e}")
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self._cache, f)
        except Exception as e:
            logger.error(f"Failed to save embedding cache: {e}")

    def get_embedding(self, text: str) -> List[float]:
        # Normalize text for cache
        clean_text = text.lower().strip()
        if clean_text in self._cache:
            return self._cache[clean_text]
        
        emb = self.embedder.embed_query(text)
        self._cache[clean_text] = emb
        self._save_cache()
        return emb

    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a * a for a in v1))
        mag2 = math.sqrt(sum(b * b for b in v2))
        if not mag1 or not mag2:
            return 0.0
        return dot_product / (mag1 * mag2)

    def search(self, query: str, index: Dict[str, List[float]], threshold: Optional[float] = None) -> List[Tuple[str, float]]:
        """
        Search for the query in the provided index.
        index: Dict mapping keys to their embeddings.
        Returns a list of (key, score) sorted by score.
        """
        if threshold is None:
            threshold = settings.embedding_similarity_threshold
            
        query_emb = self.get_embedding(query)
        matches = []

        for key, key_emb in index.items():
            score = self.cosine_similarity(query_emb, key_emb)
            if score >= threshold:
                matches.append((key, score))

        return sorted(matches, key=lambda x: x[1], reverse=True)

    def update_index(self, index: Dict[str, List[float]], keys: List[str]) -> Dict[str, List[float]]:
        """
        Ensures all keys in the list have embeddings in the index.
        """
        for key in keys:
            if key not in index:
                index[key] = self.get_embedding(key)
        return index
