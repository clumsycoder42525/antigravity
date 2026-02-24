from app.utils.logger import get_logger
from app.llm_providers.base import BaseLLM
from typing import Optional

class BaseAgent:
    def __init__(self, name: str, llm: Optional[BaseLLM] = None):
        self.name = name
        self.logger = get_logger(name)
        self.llm = llm
        self.logger.info(f"🧠 Agent Initialized: {name}")

    def set_llm(self, llm: BaseLLM):
        self.llm = llm

    def _generate(self, prompt: str, **kwargs) -> str:
        """Helper to generate text using the injected LLM or default service."""
        if self.llm:
            result = self.llm.generate(prompt, **kwargs)
            if result.get("status") == "success":
                return result["content"]
            else:
                self.logger.error(f"LLM Provider error: {result.get('error')}")
                return f"Error: {result.get('content')}"
        
        # Fallback to legacy service if no LLM injected
        from app.services.llm_service import ask_llm
        return ask_llm(prompt)
