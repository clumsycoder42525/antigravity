import logging
import httpx
import time
from typing import Any, AsyncGenerator, Dict, List, Optional
from .base import BaseLLM
from ..config.settings import settings

logger = logging.getLogger(__name__)

class OllamaLLM(BaseLLM):
    """Hardened Ollama local provider implementation."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model_name
        self.timeout = float(getattr(settings, "ollama_timeout", 10.0))
        self.max_retries = 1

    def _execute_with_retry(self, func, *args, **kwargs):
        """Internal helper for retry logic."""
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_exception = e
                if attempt < self.max_retries:
                    logger.warning(f"Ollama request failed (attempt {attempt + 1}), retrying... Error: {e}")
                    time.sleep(1)
                continue
            except httpx.HTTPStatusError as e:
                logger.error(f"Ollama HTTP error {e.response.status_code}: {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Unexpected Ollama error: {e}")
                raise
        
        raise last_exception or Exception("Ollama request failed after retries")

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response with hardening."""
        def make_request():
            with httpx.Client(timeout=self.timeout) as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.7)
                    }
                }
                response = client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
                return response.json()

        try:
            data = self._execute_with_retry(make_request)
            return {
                "status": "success",
                "content": data.get("response", ""),
                "model": f"ollama/{self.model}",
                "provider": "ollama"
            }
        except Exception as e:
            error_msg = f"Ollama generation failed: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "content": "Provider error: Ollama is unavailable or misconfigured.",
                "error": error_msg,
                "provider": "ollama"
            }

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream response with timeout handling."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": kwargs.get("temperature", 0.7)
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        logger.error(f"Ollama streaming error {response.status_code}: {error_text.decode()}")
                        yield f"Error: Ollama returned status {response.status_code}"
                        return

                    async for line in response.aiter_lines():
                        if line:
                            import json
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                                if data.get("done"):
                                    break
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Ollama streaming failed: {e}")
            yield f"Error: Connection to Ollama failed"

    def health_check(self) -> Dict[str, Any]:
        """
        Implementation of health_check() as per requirements.
        Pings /api/tags and checks if model exists.
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                if response.status_code != 200:
                    return {"provider": "ollama", "status": "unavailable", "reason": f"HTTP {response.status_code}"}
                
                data = response.json()
                models = [m.get("name") for m in data.get("models", [])]
                
                # Check if configured model exists
                status = "healthy"
                if self.model not in models:
                    logger.warning(f"Configured Ollama model '{self.model}' not found in available models: {models}")
                    # Per requirement: "If model not pulled -> return controlled configuration error"
                    # But here we return "healthy" status with models list if service is up, 
                    # specific model check can be handled by the caller or reported in status.
                    # We'll mark as unavailable if the model is missing to satisfy the "controlled configuration error"
                    return {
                        "provider": "ollama",
                        "status": "unavailable",
                        "reason": f"Model '{self.model}' not found. Please run 'ollama pull {self.model}'",
                        "models": models
                    }

                return {
                    "provider": "ollama",
                    "status": "healthy",
                    "models": models
                }
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            logger.error(f"Ollama health check failed: {e}")
            return {"provider": "ollama", "status": "unavailable", "reason": "Connection failed"}
        except Exception as e:
            logger.error(f"Ollama health check unexpected error: {e}")
            return {"provider": "ollama", "status": "unavailable", "reason": str(e)}
