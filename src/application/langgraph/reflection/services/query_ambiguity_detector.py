from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.application.workflows.retrieval.retrieval_query_intent_inferer import (
    RetrievalQueryIntentInferer,
)
from src.domain.retrieval import RetrievalQuery

if TYPE_CHECKING:
    # Deferred: a module-level import here re-enters
    # src.application.langgraph.nodes's __init__ chain, which itself
    # imports back into this reflection package -- a genuine circular
    # import. RetrievalIntentDecision is only ever used as a type
    # annotation in this module, so TYPE_CHECKING-only is sufficient.
    from src.application.langgraph.nodes.retrieval_intent_decision import (
        RetrievalIntentDecision,
    )


@dataclass(slots=True, frozen=True)
class AmbiguousIntentTie:
    intent_label: str
    runner_up_label: str


class QueryAmbiguityDetector:
    """Detects a genuine, generic query-ambiguity signal: an exact scoring
    tie between two `RetrievalQueryIntent` candidates (gap == 0 -- the same
    precise signal already used to widen chunk-type preferences on a tie,
    see RetrievalQueryAnalyzer.analyze()). Unlike the maintenance/spare-parts/
    identifier detectors, this needs no domain keyword list at all -- it
    works for any pair of intents, which is what makes it a real
    "any question" clarification trigger rather than another hardcoded
    category.

    Prefers a caller-supplied `RetrievalIntentDecision` -- the SAME
    classification that already drove retrieval (see PR 1-3,
    answering_flow_weakness_remediation_plan.md) -- over reclassifying the
    question from scratch. The `.classify()` fallback below only remains
    for callers that genuinely have no retrieval result to read a decision
    from (e.g. a bare question with no prior retrieval pass); once
    `ReflectionService.review()`, the one real caller, always supplies a
    decision, this fallback becomes dead code and should be removed."""

    def __init__(
        self,
        *,
        intent_inferer: RetrievalQueryIntentInferer | None = None,
    ) -> None:
        self._intent_inferer = intent_inferer or RetrievalQueryIntentInferer()

    def detect(
        self,
        question: str | None,
        *,
        retrieval_intent_decision: RetrievalIntentDecision | None = None,
    ) -> AmbiguousIntentTie | None:
        if retrieval_intent_decision is not None:
            if not retrieval_intent_decision.is_contested:
                return None
            return AmbiguousIntentTie(
                intent_label=_humanize(retrieval_intent_decision.intent),
                runner_up_label=_humanize(
                    retrieval_intent_decision.runner_up_intent or ""
                ),
            )
        if not question or not question.strip():
            return None
        query = RetrievalQuery(query_id="ambiguity_check", query_text=question)
        classification = self._intent_inferer.classify(query)
        if classification.runner_up_intent is None or classification.gap != 0:
            return None
        return AmbiguousIntentTie(
            intent_label=_humanize(classification.intent.value),
            runner_up_label=_humanize(classification.runner_up_intent.value),
        )


def _humanize(intent_value: str) -> str:
    return intent_value.replace("_", " ")
