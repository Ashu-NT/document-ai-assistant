from src.application.langgraph.reflection.evaluators.evidence_quality_scorer import (
    EvidenceQualityScorer,
)

_APPROVED_CHUNKS = [
    {
        "chunk_id": "chunk_1",
        "document_id": "doc_1",
        "content": "Maintenance interval is 500 hours.",
        "source": {"page_start": 12},
    }
]


def test_reference_notes_omitted_is_byte_identical_to_before_the_change() -> None:
    """Mandatory backward-compatibility test: calling score() without
    reference_notes (or with None) must produce exactly the same
    EvidenceQuality as the pre-existing 3-signal computation."""
    without_param = EvidenceQualityScorer.score(
        approved_chunks=_APPROVED_CHUNKS,
        rejected_chunks=[],
        selected_document_id="doc_1",
    )
    with_explicit_none = EvidenceQualityScorer.score(
        approved_chunks=_APPROVED_CHUNKS,
        rejected_chunks=[],
        selected_document_id="doc_1",
        reference_notes=None,
    )

    assert without_param == with_explicit_none
    assert without_param.score == 1.0
    assert without_param.issues == []


def test_evidence_with_unresolved_reference_notes_scores_lower_than_all_resolved() -> None:
    all_resolved = EvidenceQualityScorer.score(
        approved_chunks=_APPROVED_CHUNKS,
        rejected_chunks=[],
        selected_document_id="doc_1",
        reference_notes=[
            {"note_id": "r1", "claim_text": "x", "source_number": 1, "chunk_id": "chunk_1"},
            {"note_id": "r2", "claim_text": "y", "source_number": 2, "chunk_id": "chunk_1"},
        ],
    )
    one_unresolved = EvidenceQualityScorer.score(
        approved_chunks=_APPROVED_CHUNKS,
        rejected_chunks=[],
        selected_document_id="doc_1",
        reference_notes=[
            {"note_id": "r1", "claim_text": "x", "source_number": 1, "chunk_id": "chunk_1"},
            {"note_id": "r2", "claim_text": "y", "source_number": 2, "chunk_id": None},
        ],
    )

    assert all_resolved.score == 1.0
    assert one_unresolved.score < all_resolved.score
    assert "unresolved_reference_notes" in one_unresolved.issues
    assert "unresolved_reference_notes" not in all_resolved.issues


def test_evidence_with_no_reference_notes_still_scores_full_when_notes_list_is_empty() -> None:
    result = EvidenceQualityScorer.score(
        approved_chunks=_APPROVED_CHUNKS,
        rejected_chunks=[],
        selected_document_id="doc_1",
        reference_notes=[],
    )

    assert result.score == 1.0
    assert "unresolved_reference_notes" not in result.issues


def test_evidence_reference_notes_accepts_dataclass_instances_not_just_dicts() -> None:
    from dataclasses import dataclass

    @dataclass
    class _Note:
        chunk_id: str | None

    result = EvidenceQualityScorer.score(
        approved_chunks=_APPROVED_CHUNKS,
        rejected_chunks=[],
        selected_document_id="doc_1",
        reference_notes=[_Note(chunk_id=None)],
    )

    assert "unresolved_reference_notes" in result.issues
    assert result.score < 1.0
