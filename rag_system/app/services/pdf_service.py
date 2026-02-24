import os
import shutil
import logging
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..core.config import Config

logger = logging.getLogger(__name__)

class PDFService:
    """
    Service for handling PDF uploads, saving, and chunking.
    """
    def __init__(self):
        self.docs_dir = Config.DOCUMENTS_DIR
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )

    def save_and_process(self, file_content: bytes, filename: str) -> List[Dict[str, Any]]:
        """
        Saves PDF to disk, loads it, and returns chunks.
        """
        if not filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are allowed.")

        file_path = os.path.join(self.docs_dir, filename)
        
        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
            logger.info(f"Saved PDF to {file_path}")

            # Load and chunk
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            
            chunks = self.text_splitter.split_documents(pages)
            
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                processed_chunks.append({
                    "content": chunk.page_content,
                    "metadata": {
                        "source": filename,
                        "page": chunk.metadata.get("page", 0),
                        "chunk_index": i
                    }
                })
            
            logger.info(f"Successfully processed PDF into {len(processed_chunks)} chunks.")
            return processed_chunks

        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            raise
