import logging
from typing import Dict, Any, Optional, Literal
from ..config.settings import settings
from ..llm_providers.factory import LLMFactory
from ..llm_providers.base import BaseLLM

logger = logging.getLogger(__name__)

class LLMService:
    """
    LLM Service (Refactored to use Factory Pattern)
    Provides a high-level API for text generation.
    """

    def __init__(self, default_provider: Optional[Literal["groq", "ollama"]] = None):
        self.default_provider = default_provider or settings.llm_provider
        # Lazy initialization or factory call per request to support runtime overrides
        self._default_llm = None

    @property
    def default_llm(self) -> BaseLLM:
        if self._default_llm is None:
            self._default_llm = LLMFactory.create(provider=self.default_provider)
        return self._default_llm

    def generate_response(
        self, 
        prompt: str, 
        provider: Optional[Literal["groq", "ollama"]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Main entrypoint: Uses Factory to select provider.
        """
        try:
            # Resolve LLM instance (from request or default)
            llm = LLMFactory.create(provider=provider) if provider else self.default_llm
            
            logger.info(f"🔵 Generating response using provider: {provider or self.default_provider}")
            result = llm.generate(prompt, **kwargs)
            
            # Match existing response format
            if result.get("status") == "success":
                return {
                    "content": result["content"],
                    "model": result["model"],
                    "status": "success"
                }
            else:
                return {
                    "error": result.get("content", "Unknown error"),
                    "details": [result.get("error", "Unknown error")],
                    "status": "failure"
                }

        except Exception as e:
            logger.error(f"LLM Service generation failed: {e}")
            return {
                "error": "LLM service temporarily unavailable",
                "details": [str(e)],
                "status": "failure"
            }

# Singleton instance for legacy support
llm_service = LLMService()

def ask_llm(prompt: str, provider: Optional[Literal["groq", "ollama"]] = None) -> str:
    """Helper function for backward compatibility"""
    result = llm_service.generate_response(prompt, provider=provider)
    
    if result.get("status") == "success":
        return result["content"]
    
    import json
    return json.dumps(result)
