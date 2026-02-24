import chromadb
from chromadb.config import Settings as ChromaSettings
from ..config.settings import settings
from ..rag.embedder import Embedder
import logging
import uuid

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Handles:
    - Embedding storage
    - ChromaDB persistence
    - Querying
    """

    def __init__(self):
        # Persistent Chroma client
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir
        )

        # Create or load collection
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # Embedder
        self.embedder = Embedder()

        logger.info(
            f"Vector store initialized | Collection: {settings.collection_name}"
        )

    # =========================================================
    # 🔹 ADD DOCUMENTS
    # =========================================================
    def add_documents(self, texts: list[str], metadatas: list[dict] | None = None) -> int:
        """
        Embed and add documents to ChromaDB.
        """

        if not texts:
            logger.warning("No texts provided for ingestion.")
            return 0

        try:
            # Generate embeddings
            embeddings = self.embedder.embed_documents(texts)

            # Generate unique IDs
            ids = [str(uuid.uuid4()) for _ in texts]

            # Default metadata
            if metadatas is None:
                metadatas = [{"source": "uploaded"} for _ in texts]

            # Add to collection
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Added {len(texts)} documents to vector store.")

            return len(texts)

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise RuntimeError(f"Vector store insertion failed: {e}")

    # =========================================================
    # 🔹 QUERY
    # =========================================================
    def query(self, query_text: str, n_results: int = 3) -> dict:
        """
        Query the vector store.
        Returns Chroma result dictionary.
        """

        try:
            # Embed query
            query_embedding = self.embedder.embed_query(query_text)

            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

            return results

        except Exception as e:
            logger.error(f"Vector store query failed: {e}")
            raise RuntimeError(f"Vector store query error: {e}")

    # =========================================================
    # 🔹 OPTIONAL: CLEAR COLLECTION
    # =========================================================
    def clear(self):
        """
        Delete and recreate collection.
        Useful for testing.
        """
        try:
            self.client.delete_collection(settings.collection_name)

            self.collection = self.client.get_or_create_collection(
                name=settings.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

            logger.info("Vector store cleared successfully.")

        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            raise
