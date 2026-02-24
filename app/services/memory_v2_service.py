import os
import json
import logging
import shutil
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..config.settings import settings
from ..services.llm_service import llm_service
from ..rag.embedder import Embedder
import math

logger = logging.getLogger(__name__)

class MemoryV2Service:
    def __init__(self):
        self.embedder = Embedder()
        self.base_dir = "./data/users"
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_path(self, user_id: str, conversation_id: str) -> str:
        user_dir = os.path.join(self.base_dir, user_id)
        os.makedirs(user_dir, exist_ok=True)
        return os.path.join(user_dir, f"{conversation_id}.memory.json")

    def load_memory(self, user_id: str, conversation_id: str) -> Dict[str, Any]:
        path = self._get_path(user_id, conversation_id)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {
            "identity": {},
            "preferences": {},
            "tasks": {},
            "bookings": {},
            "facts": {},
            "conversation_summary": ""
        }

    def save_memory_atomically(self, user_id: str, conversation_id: str, memory: Dict[str, Any]):
        path = self._get_path(user_id, conversation_id)
        temp_path = f"{path}.tmp"
        with open(temp_path, "w") as f:
            json.dump(memory, f, indent=2)
        shutil.move(temp_path, path)
        logger.info(f"Memory persisted atomically for user {user_id}, conv {conversation_id}")

    def extract_structured_memory(self, user_id: str, conversation_id: str, text: str):
        """
        Run structured extraction pass (temperature=0).
        """
        prompt = f"""
        Extract structured information from the following user message.
        User Message: "{text}"
        
        Return a list of JSON objects with:
        - type: "identity" | "preference" | "task" | "booking" | "fact"
        - key: A unique identifier for the info (e.g., "name", "favorite_color", "current_task")
        - value: The actual information
        
        STRICT JSON list only. No other text.
        """
        
        response = llm_service.generate_response(prompt, temperature=0)
        if response.get("status") == "success":
            try:
                content = response["content"].strip()
                if content.startswith("```json"):
                    content = content.split("```json")[1].split("```")[0].strip()
                elif content.startswith("```"):
                    content = content.split("```")[1].split("```")[0].strip()
                
                extractions = json.loads(content)
                if isinstance(extractions, list):
                    memory = self.load_memory(user_id, conversation_id)
                    for item in extractions:
                        m_type = item.get("type")
                        key = item.get("key")
                        value = item.get("value")
                        if m_type and key and value and m_type in memory:
                            memory[m_type][key] = value
                    
                    self.save_memory_atomically(user_id, conversation_id, memory)
            except Exception as e:
                logger.error(f"Failed to parse memory extraction: {e}")

    def recall_memory(self, user_id: str, conversation_id: str, query: str, threshold: float = 0.7) -> Optional[str]:
        """
        Embedding-based recall.
        Compare query embedding against stored memory keys.
        """
        memory = self.load_memory(user_id, conversation_id)
        query_emb = self.embedder.embed_query(query)
        
        best_match = None
        highest_sim = -1.0
        
        # Flattened memory search
        for m_type in ["identity", "preferences", "tasks", "bookings", "facts"]:
            for key, value in memory.get(m_type, {}).items():
                key_emb = self.embedder.embed_query(key)
                sim = self._cosine_similarity(query_emb, key_emb)
                
                if sim > threshold and sim > highest_sim:
                    highest_sim = sim
                    best_match = value
        
        return best_match

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a * a for a in v1))
        mag2 = math.sqrt(sum(b * b for b in v2))
        if not mag1 or not mag2: return 0.0
        return dot_product / (mag1 * mag2)

    def get_memory_summary(self, user_id: str, conversation_id: str) -> str:
        memory = self.load_memory(user_id, conversation_id)
        summary_parts = []
        for m_type in ["identity", "preferences", "tasks", "bookings", "facts"]:
            items = memory.get(m_type, {})
            if items:
                part = f"{m_type.capitalize()}: " + ", ".join([f"{k}={v}" for k, v in items.items()])
                summary_parts.append(part)
        
        if memory.get("conversation_summary"):
            summary_parts.append(f"Summary: {memory['conversation_summary']}")
            
        return " | ".join(summary_parts) if summary_parts else "No memory stored."

    def update_conversation_summary(self, user_id: str, conversation_id: str, summary: str):
        memory = self.load_memory(user_id, conversation_id)
        memory["conversation_summary"] = summary
        self.save_memory_atomically(user_id, conversation_id, memory)
