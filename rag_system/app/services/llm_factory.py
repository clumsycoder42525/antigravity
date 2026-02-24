import os
import logging
from typing import Optional, Any
from langchain_groq import ChatGroq
from ..core.config import Config
from .ollama_service import OllamaService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMFactory:
    """
    Production-safe LLM Factory that switches between Groq and local Ollama inference.
    """
    _llm = None

    @classmethod
    def get_llm(cls):
        if cls._llm is None:
            cls._llm = cls._initialize_llm()
        return cls._llm

    @classmethod
    def _initialize_llm(cls):
        """
        Returns a wrapped LLM that tries Groq first and falls back to local Ollama.
        """
        primary_llm = None
        if Config.GROQ_API_KEY:
            try:
                logger.info(f"Initializing Groq LLM with model {Config.DEFAULT_MODEL}...")
                primary_llm = ChatGroq(
                    api_key=Config.GROQ_API_KEY,
                    model_name=Config.DEFAULT_MODEL,
                    temperature=0.7
                )
            except Exception as e:
                logger.error(f"Failed to initialize Groq LLM: {e}")

        # Ollama service for fallback
        ollama = OllamaService()
        
        # Return a fallback wrapper
        return RobustLLMWrapper(primary=primary_llm, fallback_service=ollama)

class RobustLLMWrapper:
    """
    Wraps a primary LLM (Groq) and a fallback service (Ollama)
    to handle runtime errors gracefully.
    """
    def __init__(self, primary: Optional[Any] = None, fallback_service: Optional[OllamaService] = None):
        self.primary = primary
        self.fallback = fallback_service

    def invoke(self, prompt: str, **kwargs) -> str:
        # 1. Try Groq
        if self.primary:
            try:
                response = self.primary.invoke(prompt, **kwargs)
                if hasattr(response, 'content'):
                    return response.content
                return str(response)
            except Exception as e:
                logger.error(f"Primary LLM (Groq) failed: {e}. Falling back to Ollama...")
        
        # 2. Try Ollama
        if self.fallback:
            try:
                if self.fallback.is_available():
                    return self.fallback.invoke(prompt, **kwargs)
                else:
                    logger.warning("Ollama service is not available.")
            except Exception as e:
                logger.error(f"Fallback LLM (Ollama) failed: {e}")

        # 3. Graceful fallback for API
        raise RuntimeError("No LLM services (Groq or Ollama) are available to handle the request.")
