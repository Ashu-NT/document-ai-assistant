from src.application.services.answer_generation.intent import (
    AnswerIntent,
    AnswerIntentAnalyzer,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _make_chunk(
    *,
    content: str,
    chunk_type: ChunkType = ChunkType.GENERAL,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=chunk_type,
        section_path=["Section"],
        source=SourceLocation(page_start=1, page_end=1),
    )


def test_specification_question_maps_to_specification_summary() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="specification",
        approved_chunks=[
            _make_chunk(
                content="Test pressure: 700 bar\nDesign pressure: 350 bar",
                chunk_type=ChunkType.CERTIFICATION_INFO,
            )
        ],
    )

    assert decision.intent == AnswerIntent.SPECIFICATION_SUMMARY


def test_technical_data_question_maps_to_specification_summary() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="technical data",
        approved_chunks=[_make_chunk(content="Voltage: 24 V")],
    )

    assert decision.intent == AnswerIntent.SPECIFICATION_SUMMARY


def test_maintenance_interval_question_maps_to_maintenance_summary() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="what are the maintenance interval?",
        approved_chunks=[
            _make_chunk(
                content="Maintenance interval: replace filter every 1000 hours.",
                chunk_type=ChunkType.MAINTENANCE_INTERVAL,
            )
        ],
    )

    assert decision.intent == AnswerIntent.MAINTENANCE_SUMMARY


def test_procedure_question_maps_to_procedure_steps() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="how do I replace the filter?",
        approved_chunks=[
            _make_chunk(
                content="1. Isolate the system\n2. Remove the cover\n3. Replace the filter",
                chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
            )
        ],
    )

    assert decision.intent == AnswerIntent.PROCEDURE_STEPS


def test_warning_question_maps_to_safety_warnings() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="warning",
        approved_chunks=[
            _make_chunk(
                content="Warning: disconnect power before opening the enclosure.",
                chunk_type=ChunkType.SAFETY_WARNING,
            )
        ],
    )

    assert decision.intent == AnswerIntent.SAFETY_WARNINGS


def test_fault_cause_remedy_maps_to_troubleshooting() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="fault cause remedy",
        approved_chunks=[
            _make_chunk(
                content="Fault: pump will not start\nCause: fuse failed\nRemedy: replace fuse",
                chunk_type=ChunkType.TROUBLESHOOTING,
            )
        ],
    )

    assert decision.intent == AnswerIntent.TROUBLESHOOTING


def test_certificate_question_maps_to_certification_summary() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="certificate inspection",
        approved_chunks=[
            _make_chunk(
                content="Certificate number: CER 1612\nInspection date: 29.11.2024",
                chunk_type=ChunkType.CERTIFICATION_INFO,
            )
        ],
    )

    assert decision.intent == AnswerIntent.CERTIFICATION_SUMMARY


def test_technical_specification_chunk_supports_specification_summary() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="what is available?",
        chunk_type_preferences=[ChunkType.TECHNICAL_SPECIFICATION],
        approved_chunks=[_make_chunk(content="Voltage: 24 V")],
    )

    assert decision.intent == AnswerIntent.SPECIFICATION_SUMMARY


def test_explicit_question_overrides_weak_chunk_hint() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="specification",
        chunk_type_preferences=[ChunkType.CERTIFICATION_INFO],
        approved_chunks=[
            _make_chunk(
                content="Test pressure: 700 bar\nDesign pressure: 350 bar",
                chunk_type=ChunkType.CERTIFICATION_INFO,
            )
        ],
    )

    assert decision.intent == AnswerIntent.SPECIFICATION_SUMMARY
