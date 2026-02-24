from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..config.settings import settings


class Chunker:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def split_text(self, text: str) -> list[str]:
        """Split text into chunks."""
        return self.splitter.split_text(text)
