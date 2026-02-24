from fastapi import APIRouter, HTTPException
from ..schemas.memory_schema import MemoryChatRequest
from ..services.state_manager import ConversationStateManager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
state_manager = ConversationStateManager()

@router.post("/chat/memory", tags=["Memory"])
def chat_with_memory(req: MemoryChatRequest):
    """
    Unified context-aware memory endpoint.
    Handles semantic recall, memory updates, task routing, and status.
    """
    try:
        result = state_manager.handle_message(
            user_id=req.user_id,
            conversation_id=req.conversation_id,
            text=req.question,
            provider=req.provider
        )
        if not result:
            raise HTTPException(status_code=500, detail="State engine returned empty result")
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unified memory chat failed: {e}", exc_info=True)
        return {
            "question": req.question,
            "intent": {"decision_question": req.question, "action": "error"},
            "decision_output": {"answer": "I encountered an internal error. Please try again later."},
            "sources": [],
            "mode": "chat",
            "error": str(e)
        }
