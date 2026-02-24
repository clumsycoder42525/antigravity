from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.state_manager import ConversationStateManager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
state_manager = ConversationStateManager()

class TicketRequest(BaseModel):
    user_id: str
    conversation_id: str
    question: str

@router.post("/agent/ticket", tags=["Booking Agent"])
def book_ticket(req: TicketRequest):
    """
    Multi-turn ticket booking routed through the unified state manager.
    """
    try:
        result = state_manager.handle_message(
            user_id=req.user_id,
            conversation_id=req.conversation_id,
            text=req.question
        )
        if not result:
            raise HTTPException(status_code=500, detail="Booking engine returned empty result")
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Ticket booking via state manager failed: {e}", exc_info=True)
        return {
            "question": req.question,
            "intent": {"decision_question": req.question, "action": "error"},
            "decision_output": {"answer": "I'm having trouble with your booking right now. Please try again."},
            "sources": [],
            "mode": "chat",
            "error": str(e)
        }
