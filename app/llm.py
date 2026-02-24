from app.services.llm_service import llm_service
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_core.language_models import BaseChatModel
from typing import Any, List, Optional, Dict
from langchain_core.outputs import ChatResult, ChatGeneration

class LLMAdapter:
    """
    Simple adapter to make LLM Service compatible with LangChain's invoke.
    """
    def __init__(self, llm: Optional[BaseLLM] = None):
        self.llm = llm

    def invoke(self, input: str | List[BaseMessage], **kwargs) -> AIMessage:
        prompt = input
        if isinstance(input, list):
            prompt = input[-1].content if input else ""
        elif hasattr(input, "to_string"):
            prompt = input.to_string()
        
        if self.llm:
            result = self.llm.generate(str(prompt), **kwargs)
        else:
            result = llm_service.generate_response(str(prompt), **kwargs)
        
        if result.get("status") == "success":
            return AIMessage(content=result["content"])
        else:
            import json
            return AIMessage(content=json.dumps(result))

    def __or__(self, other):
        return other

def get_llm(llm: Optional[BaseLLM] = None):
    return LLMAdapter(llm=llm)
