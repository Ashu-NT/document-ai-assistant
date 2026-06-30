from __future__ import annotations

from src.application.langgraph.research.policies import ResearchTaskPolicy
from src.application.validation.common import ValidationResult, Validator

_UNSAFE_MUTATION_MARKERS = ("delete", "reingest", "ingest", "remove", "replace")


class ResearchTaskValidator(Validator):
    def __init__(self, *, policy: ResearchTaskPolicy | None = None) -> None:
        self.policy = policy or ResearchTaskPolicy()

    def validate(self, value) -> ValidationResult:
        result = ValidationResult()
        title = getattr(value, "title", "")
        question = getattr(value, "question", "")
        strategy_hint = getattr(value, "strategy_hint", None)
        document_id = getattr(value, "document_id", None)
        max_results = getattr(value, "max_results", 0)

        if not isinstance(title, str) or not title.strip():
            result.add_issue("title", "Research task title cannot be empty.", "research.task.title.required")
        elif len(title) > self.policy.max_title_chars:
            result.add_issue("title", "Research task title is too long.", "research.task.title.too_long")

        if not isinstance(question, str) or not question.strip():
            result.add_issue("question", "Research task question cannot be empty.", "research.task.question.required")
        elif len(question) > self.policy.max_question_chars:
            result.add_issue("question", "Research task question is too long.", "research.task.question.too_long")

        lowered = f"{title} {question}".lower()
        if any(marker in lowered for marker in _UNSAFE_MUTATION_MARKERS):
            result.add_issue(
                "question",
                "Research tasks cannot describe mutation actions.",
                "research.task.question.unsafe_mutation",
            )

        if strategy_hint is not None and strategy_hint not in self.policy.allowed_strategy_hints:
            result.add_issue(
                "strategy_hint",
                "Unknown research strategy hint.",
                "research.task.strategy_hint.unknown",
            )

        if self.policy.require_document_scope and not document_id:
            result.add_issue(
                "document_id",
                "Research task requires document scope.",
                "research.task.document_id.required",
            )

        if not isinstance(max_results, int) or max_results <= 0 or max_results > self.policy.max_results:
            result.add_issue(
                "max_results",
                "Research task max_results must be within the allowed range.",
                "research.task.max_results.invalid",
            )

        return result
