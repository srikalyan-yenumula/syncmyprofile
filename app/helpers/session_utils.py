import os
import json
import uuid
import time
from typing import Optional, Dict, Any

class FilesystemSession:
    def __init__(self, session_dir: str = "data/sessions"):
        self.session_dir = session_dir
        os.makedirs(self.session_dir, exist_ok=True)

    def _get_path(self, session_id: str) -> str:
        return os.path.join(self.session_dir, f"{session_id}.json")

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.save_session(session_id, {})
        return session_id

    def get_session(self, session_id: str) -> Dict[str, Any]:
        path = self._get_path(session_id)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_session(self, session_id: str, data: Dict[str, Any]):
        path = self._get_path(session_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def delete_session(self, session_id: str):
        path = self._get_path(session_id)
        if os.path.exists(path):
            os.remove(path)

# Global instance
session_store = FilesystemSession()
