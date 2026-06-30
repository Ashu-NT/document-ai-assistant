from __future__ import annotations

from src.application.langgraph.research.models import ResearchSynthesis
from src.application.langgraph.research.synthesizers.evidence_synthesizer import (
    EvidenceSynthesizer,
)


class ComparisonSynthesizer:
    def __init__(self, *, evidence_synthesizer: EvidenceSynthesizer | None = None) -> None:
        self.evidence_synthesizer = evidence_synthesizer or EvidenceSynthesizer()

    def synthesize(self, result) -> ResearchSynthesis:
        base = self.evidence_synthesizer.synthesize(result)
        comparisons = []
        titles = [section["title"] for section in base.sections]
        if len(titles) >= 2:
            comparisons.append(
                {
                    "left": titles[0],
                    "right": titles[1],
                    "relationship": "Both topics were researched from the same selected document.",
                }
            )
        base.summary = "Comparison Summary"
        base.comparisons = comparisons
        return base
