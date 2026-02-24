import requests
import logging
from typing import Optional
from ..config.settings import settings

logger = logging.getLogger(__name__)


class OllamaService:
    """
    Service layer for local Ollama LLM inference.
    Production-safe version.
    """

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        # Never use settings in default params (import-time crash issue)
        self.base_url = base_url or getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or getattr(settings, "OLLAMA_MODEL", "llama3")
        self.timeout = getattr(settings, "OLLAMA_TIMEOUT", 60)

        self.generate_url = f"{self.base_url}/api/generate"
        self.tags_url = f"{self.base_url}/api/tags"

        logger.info(f"OllamaService initialized | Model: {self.model} | Base URL: {self.base_url}")

    # ---------------------------------------------------
    # Health Check
    # ---------------------------------------------------
    def is_available(self) -> bool:
        """Checks if the Ollama service is reachable."""
        try:
            response = requests.get(self.tags_url, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    # ---------------------------------------------------
    # Inference
    # ---------------------------------------------------
    def invoke(self, prompt: str, **kwargs) -> str:
        """
        Sends a generation request to Ollama.
        """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }

        try:
            logger.info(f"Invoking Ollama model: {self.model}")

            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=self.timeout
            )

            response.raise_for_status()

            data = response.json()

            return data.get("response", "")

        except requests.Timeout:
            logger.error("Ollama request timed out.")
            raise RuntimeError("Ollama service timeout.")

        except requests.RequestException as e:
            logger.error(f"Ollama HTTP error: {e}")
            raise RuntimeError(f"Ollama service error: {e}")

        except Exception as e:
            logger.error(f"Unexpected Ollama error: {e}")
            raise RuntimeError(f"Ollama unexpected error: {e}")
