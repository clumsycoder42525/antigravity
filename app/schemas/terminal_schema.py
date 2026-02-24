from pydantic import BaseModel
from typing import Dict, Any

class TerminalRequest(BaseModel):
    query: str
    context: Dict[str, Any] = {}

class TerminalResponse(BaseModel):
    command: str
    explanation: str
    safety_status: str
