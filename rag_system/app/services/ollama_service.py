import requests
import json
import logging
from typing import Optional, Dict, Any
from ..core.config import Config

logger = logging.getLogger(__name__)

class OllamaService:
    """
    Service for local LLM inference using Ollama API.
    """
    def __init__(self, base_url: str = Config.OLLAMA_BASE_URL, model: str = Config.OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def invoke(self, prompt: str, **kwargs) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        
        try:
            logger.info(f"Calling Ollama inference with model: {self.model}")
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama connection error: {e}")
            raise RuntimeError(f"Failed to connect to Ollama at {self.base_url}")
        except Exception as e:
            logger.error(f"Ollama unexpected error: {e}")
            raise
            
    def is_available(self) -> bool:
        """Check if Ollama service is reachable and the model is loaded."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                return any(m["name"].startswith(self.model) for m in models)
            return False
        except:
            return False
