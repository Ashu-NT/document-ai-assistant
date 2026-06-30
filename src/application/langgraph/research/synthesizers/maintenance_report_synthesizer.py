from __future__ import annotations

from src.application.langgraph.research.models import ResearchSynthesis
from src.application.langgraph.research.synthesizers.evidence_synthesizer import (
    EvidenceSynthesizer,
)


class MaintenanceReportSynthesizer:
    def __init__(self, *, evidence_synthesizer: EvidenceSynthesizer | None = None) -> None:
        self.evidence_synthesizer = evidence_synthesizer or EvidenceSynthesizer()

    def synthesize(self, result) -> ResearchSynthesis:
        base = self.evidence_synthesizer.synthesize(result)
        base.summary = "Maintenance Research Report"
        return base
