from pydantic import BaseModel
from typing import Optional, Literal

class ChatRequest(BaseModel):
    question: str
    mode: str = "chat"          # chat | summary | research
    max_lines: Optional[int] = None
    provider: Optional[Literal["groq", "ollama"]] = None
