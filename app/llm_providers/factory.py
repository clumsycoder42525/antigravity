import logging
from typing import Optional, Literal
from .base import BaseLLM
from .groq_provider import GroqLLM
from .ollama_provider import OllamaLLM
from ..config.settings import settings

logger = logging.getLogger(__name__)

class LLMFactory:
    """
    Centralized factory for creating LLM provider instances.
    Supports default resolution from settings and runtime overrides.
    """

    @staticmethod
    def create(
        provider: Optional[Literal["groq", "ollama"]] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> BaseLLM:
        """
        Create an LLM instance based on the specified provider or default settings.
        """
        target_provider = provider or settings.llm_provider
        
        logger.info(f"Creating LLM provider: {target_provider}")

        if target_provider == "groq":
            return GroqLLM(api_key=api_key, model=model)
        elif target_provider == "ollama":
            return OllamaLLM(base_url=base_url, model=model)
        else:
            logger.warning(f"Unknown provider '{target_provider}'. Falling back to Groq.")
            return GroqLLM()
