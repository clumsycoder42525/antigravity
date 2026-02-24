from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

class BaseLLM(ABC):
    """
    Abstract Base Class for all LLM providers.
    Ensures a consistent interface across different implementations.
    """

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a synchronous generation request.
        
        Args:
            prompt: User input string
            **kwargs: Additional configuration (temperature, max_tokens, etc.)
            
        Returns:
            Dict containing 'content', 'model', and 'status'.
        """
        pass

    @abstractmethod
    def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Execute a streaming generation request.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Verify if the provider is reachable and correctly configured.
        """
        pass
