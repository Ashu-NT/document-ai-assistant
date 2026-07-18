from __future__ import annotations

from typing import Protocol

from src.application.langgraph.reflection.models import SufficiencyVerdict
from src.application.langgraph.reflection.strategies.evidence_sufficiency.evidence_sufficiency_context import (
    EvidenceSufficiencyContext,
)


class EvidenceSufficiencyStrategy(Protocol):
    """Judges whether a generated answer is sufficiently supported by the
    approved evidence for one `RetrievalQueryIntent` category (or, for
    `GenericEvidenceSufficiencyStrategy`, for any category with no
    registered specialization). Replaces keyword-marker-driven context
    detectors scattered across the reflection decider/validator with one
    dispatchable interface, keyed by intent instead of re-derived per call
    site."""

    def is_answer_sufficient(
        self, context: EvidenceSufficiencyContext
    ) -> SufficiencyVerdict: ...
