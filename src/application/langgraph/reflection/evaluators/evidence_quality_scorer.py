from __future__ import annotations

from typing import Any

from src.application.langgraph.reflection.models import EvidenceQuality


def _reference_note_chunk_id(note: Any) -> str | None:
    """Read `chunk_id` off a reference note, whichever shape it arrives in --
    a serialized dict (the common case, coming off a tool-result payload) or
    a `ReferenceNote` dataclass instance (e.g. in tests that construct one
    directly)."""
    if isinstance(note, dict):
        return note.get("chunk_id")
    return getattr(note, "chunk_id", None)


class EvidenceQualityScorer:
    @staticmethod
    def score(
        *,
        approved_chunks: list[dict[str, Any]],
        rejected_chunks: list[dict[str, Any]],
        selected_document_id: str | None,
        reference_notes: list[Any] | None = None,
    ) -> EvidenceQuality:
        page_numbers: list[int] = []
        document_ids: list[str] = []
        has_document_leakage = False
        for chunk in approved_chunks:
            document_id = chunk.get("document_id")
            if document_id:
                text_id = str(document_id)
                if text_id not in document_ids:
                    document_ids.append(text_id)
                if selected_document_id is not None and text_id != selected_document_id:
                    has_document_leakage = True
            source = chunk.get("source") or {}
            if isinstance(source, dict):
                page_start = source.get("page_start")
                if isinstance(page_start, int):
                    page_numbers.append(page_start)
        has_sufficient_evidence = len(approved_chunks) > 0
        issues: list[str] = []
        if not has_sufficient_evidence:
            issues.append("no_approved_chunks")
        if has_document_leakage:
            issues.append("document_scope_leakage")

        if reference_notes is None:
            # Backward-compatible path: no reference-note signal available,
            # behavior is byte-identical to before this signal existed.
            score = round(
                (
                    (1.0 if has_sufficient_evidence else 0.0)
                    + (0.0 if has_document_leakage else 1.0)
                    + (1.0 if page_numbers else 0.0)
                )
                / 3.0,
                4,
            )
        else:
            total_notes = len(reference_notes)
            resolved_notes = sum(
                1 for note in reference_notes if _reference_note_chunk_id(note) is not None
            )
            # An answer with zero reference notes has nothing unresolved to
            # penalize -- treat that as a fully-resolved (1.0) signal rather
            # than a fully-unresolved (0.0) one.
            citation_resolution_rate = (
                (resolved_notes / total_notes) if total_notes else 1.0
            )
            if total_notes and resolved_notes < total_notes:
                issues.append("unresolved_reference_notes")
            score = round(
                (
                    (1.0 if has_sufficient_evidence else 0.0)
                    + (0.0 if has_document_leakage else 1.0)
                    + (1.0 if page_numbers else 0.0)
                    + citation_resolution_rate
                )
                / 4.0,
                4,
            )
        return EvidenceQuality(
            approved_chunk_count=len(approved_chunks),
            rejected_chunk_count=len(rejected_chunks),
            document_ids=document_ids,
            page_numbers=sorted(set(page_numbers)),
            has_document_leakage=has_document_leakage,
            has_sufficient_evidence=has_sufficient_evidence,
            score=score,
            issues=issues,
        )
