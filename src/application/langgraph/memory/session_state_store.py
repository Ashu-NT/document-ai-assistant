from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


class SessionStateStore:
    def __init__(
        self,
        *,
        storage_dir: Path | str | None = None,
        persist_to_disk: bool = True,
    ) -> None:
        self.storage_dir = Path(storage_dir or "outputs/agent_sessions")
        self.persist_to_disk = persist_to_disk
        self._states: dict[str, dict[str, Any]] = {}
        if self.persist_to_disk:
            self.storage_dir.mkdir(parents=True, exist_ok=True)

    def get(self, session_id: str) -> dict[str, Any] | None:
        state = self._states.get(session_id)
        if state is not None:
            return deepcopy(state)
        if not self.persist_to_disk:
            return None
        session_path = self._session_path(session_id)
        if not session_path.exists():
            return None
        with session_path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        if not isinstance(loaded, dict):
            return None
        self._states[session_id] = deepcopy(loaded)
        return deepcopy(loaded)

    def save(self, session_id: str, state: dict[str, Any]) -> None:
        snapshot = deepcopy(state)
        self._states[session_id] = snapshot
        if not self.persist_to_disk:
            return
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        session_path = self._session_path(session_id)
        with session_path.open("w", encoding="utf-8") as handle:
            json.dump(snapshot, handle, indent=2, ensure_ascii=True)

    def clear(self, session_id: str) -> None:
        self._states.pop(session_id, None)
        if not self.persist_to_disk:
            return
        session_path = self._session_path(session_id)
        if session_path.exists():
            session_path.unlink()

    def _session_path(self, session_id: str) -> Path:
        safe_session_id = "".join(
            char if char.isalnum() or char in {"_", "-", "."} else "_"
            for char in session_id
        )
        return self.storage_dir / f"{safe_session_id}.json"
