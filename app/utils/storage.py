import os
import json
import threading
from typing import Dict, List, Any
from pathlib import Path
from ..config.settings import settings

class Storage:
    _lock = threading.Lock()

    @staticmethod
    def _get_user_path(user_id: str) -> Path:
        path = Path(settings.memory_storage_path) / user_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _get_conversation_path(user_id: str, conversation_id: str) -> Path:
        return Storage._get_user_path(user_id) / f"{conversation_id}.json"

    @classmethod
    def save_conversation(cls, user_id: str, conversation_id: str, messages: List[Dict[str, Any]]):
        """
        Saves or updates a conversation file. Atomic and Thread-safe.
        """
        import tempfile
        file_path = cls._get_conversation_path(user_id, conversation_id)
        data = {
            "conversation_id": conversation_id,
            "messages": messages
        }
        
        with cls._lock:
            # Use atomic write: write to temp file then move
            fd, temp_path = tempfile.mkstemp(dir=file_path.parent, text=True)
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                os.replace(temp_path, file_path)
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise e

    @classmethod
    def load_conversation(cls, user_id: str, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Loads messages from a conversation file.
        """
        file_path = cls._get_conversation_path(user_id, conversation_id)
        if not file_path.exists():
            return []
        
        with cls._lock:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("messages", [])
            except (json.JSONDecodeError, IOError):
                return []

    @classmethod
    def append_message(cls, user_id: str, conversation_id: str, role: str, content: str):
        """
        Appends a message to a conversation.
        """
        from datetime import datetime
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        messages = cls.load_conversation(user_id, conversation_id)
        messages.append(message)
        cls.save_conversation(user_id, conversation_id, messages)
