from __future__ import annotations

from src.application.guardrails.models.detector_match import DetectorMatch


class CitationFailureDetector:
    def detect(self, *, answer_text: str | None, citations: list[object]) -> DetectorMatch:
        if not answer_text or not answer_text.strip():
            return DetectorMatch(matched=False)
        if citations:
            return DetectorMatch(matched=False)
        return DetectorMatch(
            matched=True,
            reason="Grounded answer is missing citations.",
        )
