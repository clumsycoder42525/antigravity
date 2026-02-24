import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..core.config import Config

class DocumentLoader:
    def __init__(self, directory=Config.DOCUMENTS_DIR):
        self.directory = directory
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )

    def load_documents(self):
        documents = []
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            return documents

        for filename in os.listdir(self.directory):
            if filename.endswith(".pdf"):
                path = os.path.join(self.directory, filename)
                text = self._extract_text_from_pdf(path)
                chunks = self.text_splitter.split_text(text)
                for i, chunk in enumerate(chunks):
                    documents.append({
                        "content": chunk,
                        "metadata": {"source": filename, "chunk": i}
                    })
        return documents

    def _extract_text_from_pdf(self, path):
        text = ""
        try:
            reader = PdfReader(path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error loading {path}: {e}")
        return text
