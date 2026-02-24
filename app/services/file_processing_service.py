import io
import pypdf
from ..rag.chunker import Chunker
from ..services.vector_store_service import VectorStoreService
import logging

logger = logging.getLogger(__name__)


class FileProcessingService:
    def __init__(self):
        self.chunker = Chunker()
        self.vector_store = VectorStoreService()

    def process_pdf(self, file_content: bytes, filename: str) -> int:
        """Process PDF content: extract text -> chunk -> index."""
        try:
            logger.info(f"Processing file: {filename}")
            
            # 1. Extract Text
            text = ""
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_content))
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            if not text.strip():
                logger.warning("No text extracted from PDF.")
                return 0

            # 2. Chunk
            chunks = self.chunker.split_text(text)
            logger.info(f"Split into {len(chunks)} chunks.")

            # 3. Store
            metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
            count = self.vector_store.add_documents(chunks, metadatas)
            
            return count

        except Exception as e:
            logger.error(f"Failed to process file {filename}: {e}")
            raise e
