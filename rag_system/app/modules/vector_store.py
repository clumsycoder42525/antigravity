import chromadb
from typing import List, Dict, Any
from ..core.config import Config

class VectorStore:
    def __init__(self, persist_directory=Config.CHROMA_PERSIST_DIR):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection("rag_documents")

    def add_documents(self, documents: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Adds multiple documents to the vector store.
        """
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def query(self, query_embedding, n_results=5):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
