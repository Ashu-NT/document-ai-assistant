from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SelectedDocumentState:
    document_id: str | None = None
    title: str | None = None
    file_name: str | None = None

    @property
    def is_selected(self) -> bool:
        return any(
            value
            for value in (
                self.document_id,
                self.title,
                self.file_name,
            )
        )

    @property
    def display_name(self) -> str | None:
        if self.title:
            return self.title
        if self.file_name:
            return Path(self.file_name).stem
        return self.document_id

    @property
    def prompt_label(self) -> str | None:
        label_source = self.display_name
        if not label_source:
            return None
        parts = str(label_source).strip().split()
        if not parts:
            return None
        return parts[0][:24]

    @classmethod
    def from_graph_data(cls, data: dict[str, Any] | None) -> "SelectedDocumentState":
        payload = data or {}
        return cls(
            document_id=_optional_str(
                payload.get("selected_document_id") or payload.get("document_id")
            ),
            title=_optional_str(
                payload.get("selected_document_title") or payload.get("document_title")
            ),
            file_name=_optional_str(payload.get("selected_document_file_name")),
        )


def _optional_str(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None
