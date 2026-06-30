from __future__ import annotations

from typing import Any

from src.application.guardrails.models.detector_match import DetectorMatch


class GroundingFailureDetector:
    def detect(
        self,
        *,
        answer_text: str | None,
        evidence_chunks: list[Any],
        selected_document_id: str | None = None,
    ) -> DetectorMatch:
        if not answer_text or not answer_text.strip():
            return DetectorMatch(matched=False)
        if not evidence_chunks:
            return DetectorMatch(
                matched=True,
                reason="Answer exists but no grounded evidence chunks were supplied.",
            )
        if selected_document_id:
            foreign_docs = {
                _extract_document_id(chunk)
                for chunk in evidence_chunks
                if _extract_document_id(chunk) not in {None, selected_document_id}
            }
            if foreign_docs:
                return DetectorMatch(
                    matched=True,
                    reason="Evidence leaked outside the selected document scope.",
                    matched_terms=sorted(str(item) for item in foreign_docs if item),
                )
        return DetectorMatch(matched=False)


def _extract_document_id(chunk: Any) -> str | None:
    if isinstance(chunk, dict):
        value = chunk.get("document_id")
    else:
        value = getattr(chunk, "document_id", None)
    return str(value) if isinstance(value, str) and value else None
