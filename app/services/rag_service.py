from ..rag.llm import LLM
from ..services.vector_store_service import VectorStoreService
import logging
import tempfile
import os

# ✅ Updated imports for latest LangChain
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)



class RAGService:
    """
    RAG Service - STRICT ISOLATION POLICY
    
    This service operates in complete isolation from external tools:
    - Uses ONLY ChromaDB for vector storage
    - Uses ONLY HuggingFace embeddings (local)
    - Uses ONLY local HuggingFace LLM (no Groq)
    - NEVER calls Wikipedia or DuckDuckGo
    - Answers STRICTLY from uploaded document context
    """
    def __init__(self):
        try:
            self.vector_store = VectorStoreService()
        except Exception as e:
            logger.error(f"Failed to initialize VectorStoreService: {e}")
            self.vector_store = None

        try:
            self.llm = LLM()  # Heavy model load
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            self.llm = None

    # =========================================================
    # 🔹 FILE INGESTION
    # =========================================================
    def ingest_uploaded_file(self, filename: str, content: bytes):

        try:
            suffix = os.path.splitext(filename)[-1].lower()

            # 1️⃣ Save temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                temp_path = tmp.name

            # 2️⃣ Load document
            if suffix == ".pdf":
                loader = PyPDFLoader(temp_path)
            else:
                loader = TextLoader(temp_path)

            documents = loader.load()

            # 3️⃣ Split into chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )

            split_docs = splitter.split_documents(documents)

            # 4️⃣ Convert Document objects → texts + metadata
            texts = [doc.page_content for doc in split_docs]
            metadatas = [doc.metadata for doc in split_docs]

            # 5️⃣ Store in vector DB
            added = self.vector_store.add_documents(texts, metadatas)

            # 6️⃣ Cleanup
            os.remove(temp_path)

            logger.info(f"Ingested {added} chunks from {filename}")

            return {
                "status": "success",
                "chunks_added": added
            }

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            raise RuntimeError(f"Ingestion error: {e}")

    # =========================================================
    # 🔹 RAG PIPELINE
    # =========================================================
    def run_rag(self, question: str) -> str:

        try:
            logger.info(f"Querying: {question}")

            if not self.vector_store:
                logger.error("Vector store not initialized.")
                return "RAG system is currently unavailable (Vector Store failed)."

            results = self.vector_store.query(question, n_results=3)
            
            # 3) Add temporary debug logging inside query method:
            print("Retrieved documents:", results)

            context = ""
            if results and results.get("documents"):
                context = "\n\n".join(results["documents"][0])

            # If no context found, return the strict message
            if not context or not context.strip():
                return "I don't know based on uploaded documents."

            prompt = f"""
You are a Retrieval-Augmented AI system.

Rules:
- Use ONLY the provided context.
- If context contains related information,
  synthesize a meaningful explanation.
- If context truly has no relevant info,
  respond:
  "I don't know based on the provided documents."

Context:
{context}

Question:
{question}

Answer clearly and logically.
"""

            logger.info("Generating answer...")
            if not self.llm:
                logger.error("LLM not initialized.")
                return "RAG system is currently unavailable (LLM failed)."

            answer = self.llm.generate(prompt)

            return answer

        except Exception as e:
            logger.error(f"RAG failed: {e}")
            return "An error occurred during RAG processing."
