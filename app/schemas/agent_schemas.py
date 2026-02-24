from pydantic import BaseModel
from typing import Optional, List, Any

class IntentRequest(BaseModel):
    question: str

class ReasoningRequest(BaseModel):
    intent_blueprint: dict
    research_data: Optional[dict] = None

class DecisionRequest(BaseModel):
    reasoning_map: dict

class DecisionOutput(BaseModel):
    executive_summary: str
    final_recommendation: str
    key_rationale: List[str]
    major_risks: List[str]
    assumptions_made: List[str]
    next_steps: List[str]
