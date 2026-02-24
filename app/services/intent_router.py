import logging
import json
from typing import Literal
from .llm_service import llm_service

logger = logging.getLogger(__name__)

IntentType = Literal["memory_update", "memory_recall", "task_start", "task_continue", "task_status", "general_chat"]

class IntentRouter:
    """
    DEPRECATED: Use ConversationStateManager._run_unified_analysis instead.
    Classifies user intent using a lightweight LLM call.
    """
    def route(self, text: str, has_active_task: bool = False) -> IntentType:
        logger.warning("IntentRouter.route is deprecated. Use unified analysis.")
        # Minimal legacy support
        return "general_chat"
