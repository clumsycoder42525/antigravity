import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from .memory_store import MemoryStore
from .embedding_manager import EmbeddingIndexManager
from .task_manager import ActiveTaskManager
from ..graphs.orchestration_graph import run_graph

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# =========================================================
# CANONICAL KEY MAP
# =========================================================
CANONICAL_KEYS = {
    "programming_language": "favorite_language",
    "destination_city": "destination",
    "study_session": "study_time",
}


# =========================================================
# CONVERSATION STATE MANAGER (PRODUCTION VERSION)
# =========================================================
class ConversationStateManager:

    def __init__(self):
        self.store = MemoryStore()
        self.embedding_manager = EmbeddingIndexManager()
        self.tasks = ActiveTaskManager()

    # =====================================================
    # ENTRY POINT
    # =====================================================
    def handle_message(
        self,
        user_id: str,
        conversation_id: str,
        text: str,
        provider: str = "groq",
    ) -> Dict[str, Any]:

        state = self._load_state(user_id, conversation_id)

        # 1️⃣ Memory Extraction
        memory_updates = self._extract_memory(text)
        if memory_updates:
            self._apply_memory_updates(state, memory_updates)
            self._persist_state(user_id, conversation_id, state)

            return self._build_response(
                text,
                "memory_update",
                "Your information has been securely stored."
            )

        # 2️⃣ Memory Recall (Robust + Structured)
        recall = self._semantic_recall(state, text)
        if recall:
            return self._build_response(
                text,
                "memory_recall",
                recall
            )

        # 3️⃣ General Chat Fallback
        answer = self._general_chat_with_context(state, text, provider)

        return self._build_response(
            text,
            "general_chat",
            answer
        )

    # =====================================================
    # LOAD STATE
    # =====================================================
    def _load_state(self, user_id: str, conversation_id: str):

        state = self.store.load(user_id, conversation_id)

        for key in ["identity", "preferences", "facts"]:
            state.setdefault(key, {})

        state.setdefault("embedding_index", {})
        return state

    # =====================================================
    # SAVE STATE
    # =====================================================
    def _persist_state(self, user_id, conversation_id, state):
        state["last_updated"] = datetime.utcnow().isoformat()
        self.store.save(user_id, conversation_id, state)

    # =====================================================
    # MEMORY EXTRACTION (STRICT JSON)
    # =====================================================
    def _extract_memory(self, text: str) -> List[Dict[str, Any]]:

        prompt = f"""
Extract personal information from the message.

Return STRICT JSON only.

Schema:
{{
  "identity": {{}},
  "preferences": {{}},
  "facts": {{}}
}}

If no personal info → return empty JSON.

Message:
{text}
"""

        try:
            from .llm_service import llm_service
            res = llm_service.generate_response(prompt, temperature=0)
            parsed = self._safe_json_parse(res.get("content", "{}"))

            updates = []

            for category in ["identity", "preferences", "facts"]:
                category_data = parsed.get(category, {})
                if isinstance(category_data, dict):
                    for key, value in category_data.items():
                        if isinstance(value, str) and value.strip():

                            normalized = CANONICAL_KEYS.get(
                                key.strip(),
                                key.strip()
                            )

                            updates.append({
                                "category": category,
                                "key": normalized,
                                "value": value.strip()
                            })

            return updates

        except Exception as e:
            logger.error(f"Memory extraction failed: {e}")
            return []

    # =====================================================
    # APPLY MEMORY UPDATES
    # =====================================================
    def _apply_memory_updates(self, state, updates):

        for item in updates:
            cat = item["category"]
            key = item["key"]
            val = item["value"]

            state[cat][key] = val

            self.embedding_manager.update_index(
                state["embedding_index"],
                [key]
            )

    # =====================================================
    # SEMANTIC RECALL (CONFIDENCE-GATED)
    # =====================================================
    def _semantic_recall(self, state, text) -> Optional[str]:

        memory = {}
        for category in ["identity", "preferences", "facts"]:
            memory.update(state.get(category, {}))

        if not memory:
            return None

        memory_block = "\n".join([f"{k}: {v}" for k, v in memory.items()])

        prompt = f"""
You are a memory reasoning engine.

Stored information:
{memory_block}

User question:
{text}

Return STRICT JSON only:

{{
  "relevant": true/false,
  "confidence": 0.0-1.0,
  "answer": "string"
}}

Rules:
- If unrelated → relevant=false
- If related → relevant=true and answer using ONLY stored data
- Do not hallucinate
"""

        try:
            from .llm_service import llm_service
            res = llm_service.generate_response(prompt, temperature=0)

            parsed = self._safe_json_parse(res.get("content", "{}"))

            if not parsed.get("relevant"):
                return None

            if parsed.get("confidence", 0) < 0.6:
                return None

            answer = parsed.get("answer", "").strip()

            if not answer:
                return None

            return answer

        except Exception as e:
            logger.error(f"Recall failure: {e}")
            return None

    # =====================================================
    # GENERAL CHAT
    # =====================================================
    def _general_chat_with_context(self, state, text, provider):

        memory = {}
        for category in ["identity", "preferences", "facts"]:
            memory.update(state.get(category, {}))

        if memory:
            memory_block = "\n".join(
                [f"{k}: {v}" for k, v in memory.items()]
            )

            text = f"""
You are a helpful assistant.

User context:
{memory_block}

Use context only if relevant.

User message:
{text}
"""

        try:
            graph_result = run_graph(
                question=text,
                mode="chat",
                provider=provider
            )

            return self._sanitize_graph_output(graph_result)

        except Exception as e:
            logger.error(f"Graph error: {e}")
            return "Something went wrong."

    # =====================================================
    # GRAPH OUTPUT SANITIZER
    # =====================================================
    def _sanitize_graph_output(self, graph_result):

        if not isinstance(graph_result, dict):
            return "No valid response generated."

        decision_output = graph_result.get("decision_output", {})

        if not isinstance(decision_output, dict):
            return "No structured output."

        for key in ["answer", "final_recommendation", "executive_summary"]:
            val = decision_output.get(key)
            if isinstance(val, str) and len(val.strip()) > 5:
                return val.strip()

        return "No answer generated."

    # =====================================================
    # SAFE JSON PARSER
    # =====================================================
    def _safe_json_parse(self, content: str):

        if not content:
            return {}

        content = content.strip()

        if "```" in content:
            content = content.split("```")[1].strip()

        try:
            return json.loads(content)
        except:
            logger.warning("Invalid JSON from LLM")
            return {}

    # =====================================================
    # RESPONSE FORMAT
    # =====================================================
    def _build_response(self, question, action, answer):

        return {
            "question": question,
            "intent": {
                "decision_question": question,
                "action": action
            },
            "decision_output": {
                "answer": answer
            },
            "sources": [],
            "mode": "chat"
        }