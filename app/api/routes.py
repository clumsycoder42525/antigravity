from fastapi import APIRouter
from pydantic import BaseModel

from ..graphs.orchestration_graph import run_graph
from ..agents.intent_agent import IntentAgent
from ..agents.reasoning_agent import ReasoningAgent
from ..agents.decision_agent import DecisionAgent
from ..agents.terminal_agent import TerminalCommandAgent, AgentContext
from ..schemas.agent_schemas import IntentRequest, ReasoningRequest, DecisionRequest
from ..schemas.terminal_schema import TerminalRequest

router = APIRouter()

# -----------------------------
# Base Schemas
# -----------------------------

from typing import Literal, Optional

class BaseRequest(BaseModel):
    question: str
    provider: Optional[Literal["groq", "ollama"]] = None

class SummaryRequest(BaseRequest):
    max_lines: int | None = None


# -----------------------------
# Core Orchestration Routes
# -----------------------------

@router.post("/chat")
def chat(req: BaseRequest):
    return run_graph(
        question=req.question,
        mode="chat",
        provider=req.provider
    )


@router.post("/intent")
def get_intent(req: IntentRequest):
    agent = IntentAgent()
    return agent.run(req.question)


@router.post("/reason")
def get_reason(req: ReasoningRequest):
    agent = ReasoningAgent()
    return agent.run(req.intent_blueprint, req.research_data)


@router.post("/decision")
def get_decision(req: DecisionRequest):
    agent = DecisionAgent()
    return agent.run(req.reasoning_map)


@router.post("/terminal")
def post_terminal(req: TerminalRequest):
    context = AgentContext(data=req.context)
    agent = TerminalCommandAgent(context)
    return agent.query(req.query)


# -----------------------------
# Legacy / Specialized Routes
# -----------------------------

@router.post("/research")
def research(req: BaseRequest):
    return run_graph(
        question=req.question,
        mode="research",
        provider=req.provider
    )


@router.post("/summary")
def summary(req: SummaryRequest):
    return run_graph(
        question=req.question,
        mode="summary",
        max_lines=req.max_lines,
        provider=req.provider
    )
