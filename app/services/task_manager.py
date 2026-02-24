import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from .llm_service import llm_service
from ..config.settings import settings

logger = logging.getLogger(__name__)

class ActiveTaskManager:
    """
    Manages active workflows and slot-filling logic.
    """
    REQUIRED_SLOTS = {
        "ticket_booking": ["type", "from", "to", "date", "class", "passenger_count"]
    }

    def process_task(self, task_state: Dict[str, Any], text: str) -> Dict[str, Any]:
        """
        Processes a turn in an active task.
        Returns a response message and the updated task state.
        """
        # Check for expiration
        if self.is_expired(task_state):
            logger.info(f"Task {task_state.get('task_id')} expired.")
            task_state["status"] = "expired"
            return {
                "message": "Your previous booking session has expired. What can I help you with today?",
                "updated_state": task_state,
                "is_complete": False,
                "expired": True
            }

        task_state["last_active"] = datetime.now().isoformat()
        task_type = task_state.get("type", "ticket_booking")
        state = task_state.get("state", {})
        
        # 1. Extract slots from user text
        new_slots = self._extract_slots(task_type, state, text)
        
        # 2. Update state
        for key, val in new_slots.items():
            if val:
                state[key] = val
        
        # 3. Check for completeness
        required = self.REQUIRED_SLOTS.get(task_type, [])
        missing = [s for s in required if not state.get(s)]
        
        if not missing:
            task_state["status"] = "completed"
            summary = self._generate_completion_summary(task_type, state)
            return {
                "message": f"Task completed! {summary}",
                "updated_state": task_state,
                "is_complete": True
            }
        
        # 4. Prompt for next slot
        next_slot = missing[0]
        prompt_msg = self._get_slot_question(next_slot)
        task_state["status"] = "in_progress"
        task_state["state"] = state
        
        return {
            "message": prompt_msg,
            "updated_state": task_state,
            "is_complete": False
        }

    def _extract_slots(self, task_type: str, current_state: Dict[str, Any], text: str) -> Dict[str, Any]:
        prompt = f"""
        Extract slots for a {task_type} task from the message: "{text}"
        Current State: {json.dumps(current_state)}
        Expected Slots: {self.REQUIRED_SLOTS.get(task_type)}
        
        Example Input: "I want to book a flight from Berlin"
        Example Output: {{ "from": "Berlin", "type": "flight" }}
        
        Return a JSON object with only the extracted slot key-value pairs. Return null for missing slots.
        STRICT JSON ONLY. No explanation.
        """
        try:
            res = llm_service.generate_response(prompt, temperature=0)
            content = res.get("content", "{}").strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"Slot extraction failed: {e}")
            return {}

    def _get_slot_question(self, slot: str) -> str:
        questions = {
            "type": "What kind of ticket are you booking (flight, train, bus)?",
            "from": "Where are you traveling from?",
            "to": "Where are you traveling to?",
            "date": "When is the travel date?",
            "class": "Which class would you like (Economy, Business, First)?",
            "passenger_count": "How many passengers?"
        }
        return questions.get(slot, f"Please provide the {slot}.")

    def _generate_completion_summary(self, task_type: str, state: Dict[str, Any]) -> str:
        if task_type == "ticket_booking":
            return f"Your {state.get('type')} booking from {state.get('from')} to {state.get('to')} on {state.get('date')} for {state.get('passenger_count')} passengers has been processed."
        return "Task processed successfully."

    def initialize_task(self, task_type: str, text: str) -> Tuple[Dict[str, Any], str]:
        """
        Initializes a new task state based on initial user text.
        """
        initial_state = {s: None for s in self.REQUIRED_SLOTS.get(task_type, [])}
        task_state = {
            "task_id": str(uuid.uuid4()),
            "type": task_type,
            "state": initial_state,
            "status": "in_progress",
            "last_active": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        # Run process_task once to capture any initial slots
        result = self.process_task(task_state, text)
        return result["updated_state"], result["message"]

    def is_expired(self, task_state: Dict[str, Any]) -> bool:
        """
        Checks if a task has expired based on inactivity.
        """
        if task_state.get("status") != "in_progress":
            return False
            
        last_active_str = task_state.get("last_active")
        if not last_active_str:
            return False
            
        try:
            last_active = datetime.fromisoformat(last_active_str)
            delta = datetime.now() - last_active
            return delta.total_seconds() > (settings.memory_task_expiry_minutes * 60)
        except Exception as e:
            logger.error(f"Error checking task expiration: {e}")
            return False
