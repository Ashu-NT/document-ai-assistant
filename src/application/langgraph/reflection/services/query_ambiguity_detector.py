from __future__ import annotations

from dataclasses import dataclass

from src.application.workflows.retrieval.retrieval_query_intent_inferer import (
    RetrievalQueryIntentInferer,
)
from src.domain.retrieval import RetrievalQuery


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
    category."""

    def __init__(
        self,
        *,
        intent_inferer: RetrievalQueryIntentInferer | None = None,
    ) -> None:
        self._intent_inferer = intent_inferer or RetrievalQueryIntentInferer()

    def detect(self, question: str | None) -> AmbiguousIntentTie | None:
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
