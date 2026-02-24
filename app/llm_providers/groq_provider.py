import logging
from typing import Any, AsyncGenerator, Dict, List, Optional
from .base import BaseLLM
from ..config.settings import settings

logger = logging.getLogger(__name__)

class GroqLLM(BaseLLM):
    """Groq API provider implementation."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.groq_api_key
        self.model = model or settings.default_model
        self.client = None
        
        if not self.api_key:
            logger.error("Groq API key is missing. GroqLLM will not function.")
            return

        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        except ImportError:
            logger.error("Groq package not installed. Run 'pip install groq'.")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        if not self.client:
            return {
                "status": "error",
                "content": "Groq provider not configured",
                "error": "Missing API key or client initialization failed"
            }

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2048)
            )
            return {
                "status": "success",
                "content": response.choices[0].message.content,
                "model": f"groq/{self.model}"
            }
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            return {
                "status": "error",
                "content": "Groq generation failed",
                "error": str(e)
            }

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        if not self.client:
            yield "Groq provider not configured"
            return

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                temperature=kwargs.get("temperature", 0.7),
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Groq streaming failed: {e}")
            yield f"Error: {str(e)}"

    def health_check(self) -> bool:
        if not self.client or not self.api_key:
            return False
        try:
            # Minimal call to check connectivity
            self.client.models.list()
            return True
        except Exception:
            return False
