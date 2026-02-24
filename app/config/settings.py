from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    # ==================================================
    # 🔹 LLM CONFIGURATION (Production Refactored)
    # ==================================================
    llm_provider: Literal["groq", "ollama"] = "groq"
    
    # Groq Config
    groq_api_key: str = ""
    default_model: str = "llama-3.1-8b-instant"

    # Ollama Config
    ollama_base_url: str = "http://localhost:11434"
    ollama_model_name: str = "phi3:mini"
    ollama_timeout: int = 60

    # ==================================================
    # 🔹 LEGACY / OTHER CONFIG (Internal use)
    # ==================================================
    # RAG CONFIG
    embedding_model_name: str = "all-MiniLM-L6-v2"
    llm_model_name: str = "google/flan-t5-base"  # Local fallback model name

    chroma_persist_dir: str = "./chroma_store"
    collection_name: str = "rag_documents"

    chunk_size: int = 500
    chunk_overlap: int = 50

    # Timing and timeouts
    llm_timeout: int = 30

    # ==================================================
    # 🔹 MEMORY & EVALUATION CONFIGURATION
    # ==================================================
    memory_enabled: bool = True
    memory_max_messages: int = 10
    memory_storage_path: str = "./data/users"
    embedding_similarity_threshold: float = 0.7
    memory_task_expiry_minutes: int = 30
    memory_embedding_cache_path: str = "./data/cache/embeddings.json"
    evaluation_enabled: bool = True

    # ==================================================
    # 🔹 Pydantic Settings Config
    # ==================================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def GROQ_API_KEY(self) -> str:
        """Backward compatibility for legacy code."""
        return self.groq_api_key

    @property
    def DEFAULT_MODEL(self) -> str:
        """Backward compatibility for legacy code."""
        return self.default_model


settings = Settings()
