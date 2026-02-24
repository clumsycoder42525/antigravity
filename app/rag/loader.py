import os
import logging
from langchain_community.document_loaders import (
    PyPDFLoader, 
    TextLoader, 
    Docx2txtLoader
)

logger = logging.getLogger(__name__)

class DocumentLoader:
    """Enterprise-grade loader supporting multiple document formats."""
    
    @staticmethod
    def get_loader(file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return PyPDFLoader(file_path)
        elif ext == ".txt":
            return TextLoader(file_path, encoding="utf-8")
        elif ext in [".docx", ".doc"]:
            return Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    def load(self, file_path: str):
        try:
            logger.info(f"Loading document: {file_path}")
            loader = self.get_loader(file_path)
            return loader.load()
        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}")
            raise
