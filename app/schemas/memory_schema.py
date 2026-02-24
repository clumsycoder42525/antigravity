from pydantic import BaseModel
from typing import Optional, Literal

class MemoryChatRequest(BaseModel):
    user_id: str
    conversation_id: str
    question: str
    provider: Optional[Literal["groq", "ollama"]] = None
