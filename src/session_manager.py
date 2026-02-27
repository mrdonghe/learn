import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class SessionManager:
    SESSION_FILE = ".session_state.json"

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.session_file = project_path / self.SESSION_FILE

    def load_session(self) -> Dict[str, Any]:
        if not self.session_file.exists():
            return self._default_session()

        with open(self.session_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _default_session(self) -> Dict[str, Any]:
        return {
            "session_id": 0,
            "last_session_time": None,
            "context_window_count": 0,
            "total_tokens_used": 0,
            "session_history": [],
        }

    def save_session(self, session: Dict[str, Any]):
        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

    def start_new_session(self) -> int:
        session = self.load_session()
        session["session_id"] += 1
        session["last_session_time"] = datetime.now().isoformat()
        self.save_session(session)
        return session["session_id"]

    def increment_context_window(self):
        session = self.load_session()
        session["context_window_count"] += 1
        self.save_session(session)

    def add_to_history(self, entry: Dict[str, Any]):
        session = self.load_session()
        entry["timestamp"] = datetime.now().isoformat()
        session["session_history"].append(entry)

        if len(session["session_history"]) > 100:
            session["session_history"] = session["session_history"][-100:]

        self.save_session(session)

    def get_session_count(self) -> int:
        return self.load_session()["session_id"]

    def get_context_window_count(self) -> int:
        return self.load_session()["context_window_count"]

    def get_last_session_time(self) -> Optional[str]:
        return self.load_session().get("last_session_time")

    def should_compact_context(self, threshold: int = 10) -> bool:
        session = self.load_session()
        return session["context_window_count"] >= threshold
