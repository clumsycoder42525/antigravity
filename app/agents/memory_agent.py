import json
import re
from typing import List, Dict, Any, Optional
from .base_agent import BaseAgent
from .summarization_agent import SummarizationAgent
from ..utils.storage import Storage
from ..config.settings import settings

class MemoryAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__("MemoryAgent", llm=llm)
        self.summarizer = SummarizationAgent()
        if llm:
            self.summarizer.set_llm(llm)

    def detect_memory_update(self, text: str) -> Optional[Dict[str, str]]:
        """
        Detects personal memory update statements including generic slots.
        No LLM allowed.
        """
        text_lower = text.lower().strip().strip("?!.")
        
        # 1. Specific Patterns
        pattern_rules = [
            ("age", [r"i am (\d+) years old", r"my age is (\d+)", r"i'm (\d+) years old"]),
            ("location", [r"i live in (.*)", r"i am from (.*)", r"my city is (.*)"]),
            ("certificate", [r"i (?:got|completed|have) (.*) (?:certificate|certification)", r"my (?:certificate|certification) is (.*)"]),
            ("project", [r"i am working on (.*) project", r"working on (.*)", r"my project is (.*)"]),
            ("exam_date", [r"my exam is on (.*)", r"i have an exam on (.*)"]),
            ("job", [r"my job is (.*)", r"i work as (?:a |an )?(.*)", r"i am (?:a |an )?(.* intern)"]),
            ("name", [r"my name is (.*)", r"call me (.*)", r"i am (.*)"]),
        ]
        
        for key, patterns in pattern_rules:
            for p in patterns:
                match = re.search(p, text_lower)
                if match:
                    val = match.group(1).strip(" .")
                    # Validation for Name
                    if key == "name" and (len(val.split()) > 2 or "working" in val or "living" in val):
                        continue
                    return {"type": key, "value": val, "original": text}

        # 2. Generic pattern: "My <slot> is <value>"
        # Using a more restrictive regex to avoid capturing conversational filler
        generic_match = re.search(r"^my ([\w\s]{1,20}) is (.*)$", text_lower)
        if generic_match:
            slot = generic_match.group(1).strip().replace(" ", "_").lower()
            val = generic_match.group(2).strip(" .")
            # Filter out common non-memory words as slots
            if slot not in ["problem", "issue", "question", "request", "goal"]:
                return {"type": slot, "value": val, "original": text}

        return None

    def detect_memory_recall(self, text: str) -> Optional[Dict[str, str]]:
        """
        Detects recall-type queries using regex + intent keywords.
        No LLM allowed.
        """
        text_lower = text.lower().strip().strip("?!.")
        
        # Identity
        if any(p in text_lower for p in ["what is my name", "who am i", "tell me my name"]):
            return {"requested_slot": "name"}
        
        # Age
        if any(p in text_lower for p in ["how old am i", "what is my age", "did i tell you my age"]):
            return {"requested_slot": "age"}
            
        # Location
        if any(p in text_lower for p in ["where do i live", "which city did i mention"]):
            return {"requested_slot": "location"}

        # Task/Specific
        patterns = {
            "certificate": [r"what certificate", r"what certification", r"my certificate", r"my certification"],
            "exam_date": [r"when is my exam", r"my exam date"],
            "project": [r"what project", r"my project"],
            "job": [r"what is my job", r"what do i do", r"my job"]
        }

        for slot, regexes in patterns.items():
            for r in regexes:
                if re.search(r, text_lower):
                    return {"requested_slot": slot}

        # Generic Recall Patterns
        # "What did I tell you about X?"
        generic_recall = re.search(r"what did i tell you about (?:my )?([\w\s]+)", text_lower)
        if generic_recall:
            slot = generic_recall.group(1).strip().replace(" ", "_").lower()
            return {"requested_slot": slot}
            
        # "Do you remember my X?"
        remember_recall = re.search(r"do you remember my ([\w\s]+)", text_lower)
        if remember_recall:
            slot = remember_recall.group(1).strip().replace(" ", "_").lower()
            return {"requested_slot": slot}

        # "What was my X?"
        was_recall = re.search(r"what was my ([\w\s]+)", text_lower)
        if was_recall:
            slot = was_recall.group(1).strip().replace(" ", "_").lower()
            return {"requested_slot": slot}

        # Fuzzy wording: "Remind me what I said about my X"
        remind_recall = re.search(r"remind me .* about (?:my )?([\w\s]+)", text_lower)
        if remind_recall:
            slot = remind_recall.group(1).strip().replace(" ", "_").lower()
            return {"requested_slot": slot}
            
        # "You remember my X (right)?" or "You know my X?"
        fuzzy_remember = re.search(r"(?:you )?(?:remember|know) (?:my )?([\w\s]+)", text_lower)
        if fuzzy_remember:
            slot = fuzzy_remember.group(1).split()[0].strip().replace(" ", "_").lower()
            # Split and take first word if it looks like a slot, or just take the whole thing if it's short
            # Actually split might break "favorite food". Let's be smarter.
            slot = fuzzy_remember.group(1).strip(" .?").replace("right", "").strip()
            slot = slot.replace(" ", "_").lower()
            return {"requested_slot": slot}

        return None

    def _extract_slots_from_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Parses conversation history and builds a structured memory dictionary.
        Latest mentions override previous values.
        """
        slots = {}
        for msg in messages:
            if msg.get("role") == "user":
                update = self.detect_memory_update(msg["content"])
                if update:
                    # Generic slot normalization: spaces to underscores, lowercase
                    key = update["type"].lower().replace(" ", "_")
                    slots[key] = update["value"]
        
        # Handle synonyms/normalization
        if "certification" in slots and "certificate" not in slots:
            slots["certificate"] = slots["certification"]
        elif "certificate" in slots and "certification" not in slots:
            slots["certification"] = slots["certificate"]
            
        return slots

    def generate_recall_response(self, slot: str, slots: Dict[str, str]) -> str:
        """
        Generates a direct factual answer based on extracted slots.
        """
        # Normalization for lookup
        lookup_key = slot.lower().replace(" ", "_")
        val = slots.get(lookup_key)
        
        if not val:
            # Try fuzzy matching in slots (e.g. "cert" matches "certificate")
            for k, v in slots.items():
                if lookup_key in k or k in lookup_key:
                    val = v
                    slot = k # Update slot to the actual key found
                    break
        
        if not val:
            return "I don't have that information yet."

        slot_label = slot.replace("_", " ")
        if slot == "name":
            return f"Your name is {val.strip().title()}."
        elif slot == "age":
            return f"You are {val} years old."
        elif slot == "location":
            return f"You live in {val.strip().title()}."
        elif "exam" in slot:
            return f"Your exam is on {val}."
        elif slot == "certificate" or slot == "certification":
            return f"You mentioned {val}."
        elif slot == "project":
            return f"You said you are working on {val}."
        elif slot == "job":
            return f"You mentioned your job is {val}."
        
        return f"You mentioned that your {slot_label} is {val}."

    def generate_acknowledgement(self, memory_info: Dict[str, str]) -> str:
        """
        Generates a clean acknowledgement for memory updates.
        """
        m_type = memory_info["type"]
        val = memory_info["value"]
        
        if m_type == "name":
            return f"Nice to meet you, {val.capitalize()}. I'll remember that."
        elif m_type == "age":
            return f"Got it. You are {val} years old."
        elif m_type == "location":
            return f"Understood. You live in {val.title()}."
        
        return f"I've noted that your {m_type.replace('_', ' ')} is {val}."

    def get_contextual_history(self, user_id: str, conversation_id: str) -> str:
        """
        Retrieves and formats conversation history for injection.
        Handles summarization if history is too long.
        """
        if not settings.memory_enabled:
            return ""

        messages = Storage.load_conversation(user_id, conversation_id)
        if not messages:
            return ""

        max_history = settings.memory_max_messages
        recent_messages = messages[-max_history:]
        
        # If there's a lot of history, summarize the older parts
        summary = ""
        if len(messages) > max_history * 2:
            older_messages = messages[:-max_history]
            summary_content = "\n".join([f"{m['role']}: {m['content']}" for m in older_messages])
            summary = self.summarizer.run({"content": summary_content}, max_lines=5)
            summary = f"Summary of previous context: {summary}\n\n"

        history_str = "Recent Conversation History:\n"
        for msg in recent_messages:
            history_str += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
        return f"{summary}{history_str}"

    def run_with_memory(self, user_id: str, conversation_id: str, user_message: str, agent_to_wrap: BaseAgent) -> str:
        """
        Injects memory context and runs the wrapped agent.
        Saves the interaction to storage.
        """
        # 1. Load context
        history_context = self.get_contextual_history(user_id, conversation_id)
        
        # 2. Prepare prompt with memory
        full_prompt = f"{history_context}\nCurrent User Message: {user_message}\n"
        
        # 3. Store user message
        Storage.append_message(user_id, conversation_id, "user", user_message)
        
        # 4. Generate response using the wrapped agent (or direct LLM if preferred)
        # Note: We use the wrapped agent's logic but provide the context-rich prompt
        if hasattr(agent_to_wrap, "ask"):
             response = agent_to_wrap.ask(full_prompt)
        elif hasattr(agent_to_wrap, "run"):
             # For agents that take specific args, we might need more complex wrapping
             # But for a general /chat, we usually want a simple generation
             response = self._generate(full_prompt)
        else:
             response = self._generate(full_prompt)

        # 5. Store system response
        Storage.append_message(user_id, conversation_id, "assistant", response)
        
        return response
