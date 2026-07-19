from src.application.services.answer_generation import AnswerIntent
from src.application.workflows.question_answering.answer_context import (
    AnswerContextOrganizer,
)
from src.application.workflows.question_answering.answer_context.evidence_contradiction_detector import (
    EvidenceConflict,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


class _FakeContradictionDetector:
    def __init__(self, conflicts: list[EvidenceConflict]) -> None:
        self._conflicts = conflicts
        self.calls = 0

    def detect(self, *, key_values, maintenance_entries) -> list[EvidenceConflict]:
        self.calls += 1
        return self._conflicts


def _make_chunk(chunk_id: str = "chunk_001") -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content="Operating pressure: 6 bar.",
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        section_path=["Specs"],
        source=SourceLocation(page_start=1, page_end=1),
    )


def test_organize_attaches_detected_conflicts_to_diagnostics() -> None:
    """PR 10 (answering_flow_weakness_remediation_plan.md, W4): contradiction
    detection runs once during evidence assembly and its result is attached
    to the existing StructuredAnswerContext.diagnostics container -- not a
    new field, not recomputed per renderer."""
    conflict = EvidenceConflict(
        key="operating pressure",
        field_kind="specification",
        values=("6 bar", "8 bar"),
        source_numbers=(1, 2),
    )
    detector = _FakeContradictionDetector([conflict])
    organizer = AnswerContextOrganizer(evidence_contradiction_detector=detector)

    context = organizer.organize(
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        chunks=[_make_chunk()],
    )

    assert detector.calls == 1
    assert context.diagnostics["has_critical_evidence_conflict"] is True
    assert context.diagnostics["evidence_conflicts"] == [
        {
            "key": "operating pressure",
            "field_kind": "specification",
            "values": ["6 bar", "8 bar"],
            "source_numbers": [1, 2],
            "is_critical": True,
        }
    ]


def test_organize_reports_no_conflict_when_the_detector_finds_none() -> None:
    detector = _FakeContradictionDetector([])
    organizer = AnswerContextOrganizer(evidence_contradiction_detector=detector)

    context = organizer.organize(
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        chunks=[_make_chunk()],
    )

    assert context.diagnostics["has_critical_evidence_conflict"] is False
    assert context.diagnostics["evidence_conflicts"] == []


def test_organize_uses_a_real_detector_by_default() -> None:
    organizer = AnswerContextOrganizer()

    context = organizer.organize(
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        chunks=[_make_chunk()],
    )

    assert context.diagnostics["has_critical_evidence_conflict"] is False
