from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class ClarificationContext:
    """Everything a `ClarificationStrategy` needs to propose clarification
    options -- bundled for the same reason as the other strategy contexts
    in this package."""

    original_user_input: str
    answer_intent: str | None
    selected_document_id: str | None
    missing_information: list[str] = field(default_factory=list)
