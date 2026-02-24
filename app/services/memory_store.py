import os
import json
import logging
import shutil
import threading
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from ..config.settings import settings

logger = logging.getLogger(__name__)

class MemoryStore:
    """
    Handles persistent JSON storage for conversation state.
    Ensures atomic writes and thread-safe access.
    """
    _lock = threading.Lock()

    def __init__(self, base_path: str = "./data/state"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_path(self, user_id: str, conversation_id: str) -> Path:
        user_dir = self.base_path / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / f"{conversation_id}.state.json"

    def load(self, user_id: str, conversation_id: str) -> Dict[str, Any]:
        """
        Loads the conversation state from disk.
        """
        path = self._get_path(user_id, conversation_id)
        if not path.exists():
            return self._get_default_state(conversation_id)

        with self._lock:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load state for {user_id}/{conversation_id}: {e}")
                return self._get_default_state(conversation_id)

    def save(self, user_id: str, conversation_id: str, state: Dict[str, Any]):
        """
        Saves the conversation state atomically.
        """
        path = self._get_path(user_id, conversation_id)
        temp_path = path.with_suffix(".tmp")
        
        with self._lock:
            try:
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2, ensure_ascii=False)
                os.replace(temp_path, path)
                logger.info(f"State persisted for {user_id}/{conversation_id}")
            except Exception as e:
                logger.error(f"Failed to save state for {user_id}/{conversation_id}: {e}")
                if temp_path.exists():
                    os.remove(temp_path)

    def _get_default_state(self, conversation_id: str) -> Dict[str, Any]:
        return {
            "conversation_id": conversation_id,
            "identity": {},
            "preferences": {},
            "facts": {},
            "active_task": {
                "type": None,
                "state": {},
                "status": "none"
            },
            "conversation_summary": "",
            "embedding_index": {}, # key -> embedding
            "message_count": 0,
            "version": 1.0,
            "last_updated": datetime.now().isoformat()
        }
