from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.application.agent_runtime.session.conversation_history import ConversationHistory
from src.application.agent_runtime.session.selected_document_state import SelectedDocumentState


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class RuntimeOptions:
    quiet: bool = False
    no_examples: bool = False
    help_examples: bool = False
    show_react: bool = False
    deep_research: bool = False
    reflection: bool = False
    llm_planning: bool = False
    retrieval_strategy: bool = False
    write_trace: bool = False
    debug: bool = False
    json_output: bool = False


@dataclass(slots=True)
class Session:
    session_id: str
    selected_document: SelectedDocumentState = field(default_factory=SelectedDocumentState)
    conversation_history: ConversationHistory = field(default_factory=ConversationHistory)
    pending_clarification: dict[str, Any] | None = None
    runtime_options: RuntimeOptions = field(default_factory=RuntimeOptions)
    last_route: str | None = None
    last_trace: Any | None = None
    last_research_plan: dict[str, Any] | None = None
    last_retrieval_strategy: dict[str, Any] | None = None
    last_context_chunks: list[dict[str, Any]] = field(default_factory=list)
    last_citations: list[dict[str, Any]] = field(default_factory=list)
    last_result: Any | None = None
    started_at: str = field(default_factory=_utc_now_iso)
    updated_at: str = field(default_factory=_utc_now_iso)

    def prompt_text(self) -> str:
        if self.pending_clarification:
            return "document-agent (clarification)>"
        label = self.selected_document.prompt_label
        if label:
            return f"document-agent [{label}]>"
        return "document-agent>"

    def touch(self) -> None:
        self.updated_at = _utc_now_iso()

    def clear_document(self) -> None:
        self.selected_document = SelectedDocumentState()
        self.pending_clarification = None
        self.touch()

    def reset_runtime_state(self) -> None:
        self.selected_document = SelectedDocumentState()
        self.conversation_history.clear()
        self.pending_clarification = None
        self.last_route = None
        self.last_trace = None
        self.last_research_plan = None
        self.last_retrieval_strategy = None
        self.last_context_chunks = []
        self.last_citations = []
        self.last_result = None
        self.touch()
