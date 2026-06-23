from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.services.document_exploration.document_exploration_result import (
    DocumentExplorationResult,
)
from src.application.workflows.question_answering.question_answering_route import (
    QuestionAnsweringRoute,
)
from src.application.workflows.retrieval.retrieval_workflow_result import (
    RetrievalWorkflowResult,
)


@dataclass(slots=True)
class QuestionAnsweringResult:
    route: QuestionAnsweringRoute

    answer_text: str | None = None
    safe_user_message: str | None = None

    guardrail_decision: GuardrailDecision | None = None
    guardrail_result: GuardrailResult | None = None

    document_exploration_result: DocumentExplorationResult | None = None
    retrieval_result: RetrievalWorkflowResult | None = None

    approved_chunk_ids: list[str] = field(default_factory=list)
    rejected_chunk_ids: list[str] = field(default_factory=list)
    citations: list[Any] = field(default_factory=list)

    confidence: str | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)
