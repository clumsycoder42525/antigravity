import logging
from typing import List, Dict, Any
from .modules.embeddings import EmbeddingProvider
from .modules.vector_store import VectorStore
from .modules.retriever import Retriever
from .services.llm_factory import LLMFactory
from .services.pdf_service import PDFService
from .core.config import Config

logger = logging.getLogger(__name__)

class RAGAgent:
    """
    RAG Agent orchestrator for document ingestion and retrieval-augmented generation.
    """
    def __init__(self):
        self.embeddings = EmbeddingProvider()
        self.vector_store = VectorStore()
        self.retriever = Retriever(self.vector_store, self.embeddings)
        self.pdf_service = PDFService()
        self.llm = LLMFactory.get_llm()

    def ingest_pdf(self, file_content: bytes, filename: str):
        """
        Ingests a PDF file: saves, chunks, embeds, and stores.
        """
        logger.info(f"Ingesting PDF: {filename}")
        chunks = self.pdf_service.save_and_process(file_content, filename)
        
        contents = [c["content"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        ids = [f"{filename}_{i}" for i in range(len(chunks))]
        
        embeddings = self.embeddings.generate_embeddings(contents)
        
        logger.info(f"Storing {len(chunks)} chunks in vector store.")
        self.vector_store.add_documents(
            documents=contents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        return len(chunks)

    def ask(self, query: str) -> str:
        """
        Retrieves context and generates an answer using the LLM (Groq with Ollama fallback).
        """
        logger.info(f"Querying RAG system: {query}")
        context_docs = self.retriever.retrieve(query)
        
        context_text = "\n\n".join([
            f"--- Source: {doc['metadata'].get('source', 'Unknown')} ---\n{doc['page_content']}"
            for doc in context_docs
        ])

        prompt = f"""
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

CONTEXT:
{context_text}

QUESTION: 
{query}

ANSWER:
"""
        logger.info("Generating response from LLM...")
        try:
            return self.llm.invoke(prompt)
        except Exception as e:
            logger.error(f"RAG answering failed: {e}")
            return "I'm sorry, I'm currently unable to process your request due to an internal error."
