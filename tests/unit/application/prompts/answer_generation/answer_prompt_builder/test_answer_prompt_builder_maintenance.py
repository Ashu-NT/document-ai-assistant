from src.application.prompts.answer_generation import AnswerPromptBuilder
from src.application.services.answer_generation import AnswerFormatPolicy, AnswerIntent
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.workflows.question_answering.answer_context import (
    AnswerContextOrganizer,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _make_chunk(
    chunk_id: str = "chunk_001",
    content: str = "Replace hydraulic filter every 1000 hours.",
    section_path: list[str] | None = None,
    page_start: int | None = 5,
    page_end: int | None = 5,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path=section_path or ["Maintenance Schedule"],
        source=SourceLocation(page_start=page_start, page_end=page_end),
    )


def test_maintenance_prompt_includes_not_specified_for_missing_intervals() -> None:
    builder = AnswerPromptBuilder()
    chunk = _make_chunk(
        content="Inspect the feed water pressure gauge.",
        section_path=["Maintenance", "Checklist"],
    )
    structured_context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        chunks=[chunk],
    )
    request = AnswerGenerationRequest(
        question="What are maintenance tasks?",
        context_chunks=[chunk],
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        structured_context=structured_context,
        format_policy=AnswerFormatPolicy.resolve(
            intent=AnswerIntent.MAINTENANCE_SUMMARY,
            structured_context=structured_context,
        ),
    )

    prompt = builder.build(request)

    assert '"maintenance_entries"' in prompt
    assert '"task": "Inspect the feed water pressure gauge"' in prompt
    assert '"interval": "Not specified"' in prompt
    assert '"component": "feed water pressure gauge"' in prompt


def test_maintenance_prompt_includes_not_specified_for_missing_component() -> None:
    builder = AnswerPromptBuilder()
    chunk = _make_chunk(
        content="Lubricate every 1000 operating hours.",
        section_path=["Maintenance", "Lubrication"],
    )
    structured_context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        chunks=[chunk],
    )
    request = AnswerGenerationRequest(
        question="What are the maintenance tasks?",
        context_chunks=[chunk],
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        structured_context=structured_context,
        format_policy=AnswerFormatPolicy.resolve(
            intent=AnswerIntent.MAINTENANCE_SUMMARY,
            structured_context=structured_context,
        ),
    )

    prompt = builder.build(request)

    assert '"task": "Lubricate"' in prompt
    assert '"interval": "every 1000 operating hours"' in prompt
    assert '"component": "Not specified"' in prompt


def test_maintenance_prompt_merges_duplicate_tasks_and_keeps_multiple_references() -> None:
    builder = AnswerPromptBuilder()
    chunks = [
        _make_chunk(
            chunk_id="chunk_a",
            content="Check gearbox every 6 months.",
            section_path=["Preventive Maintenance", "Gearbox"],
            page_start=45,
            page_end=45,
        ),
        _make_chunk(
            chunk_id="chunk_b",
            content="Check gearbox for leaks every 6 months.",
            section_path=["Preventive Maintenance", "Lubrication"],
            page_start=46,
            page_end=46,
        ),
    ]
    structured_context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        chunks=chunks,
    )
    request = AnswerGenerationRequest(
        question="What are the maintenance tasks?",
        context_chunks=chunks,
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        structured_context=structured_context,
        format_policy=AnswerFormatPolicy.resolve(
            intent=AnswerIntent.MAINTENANCE_SUMMARY,
            structured_context=structured_context,
        ),
    )

    prompt = builder.build(request)

    assert len(structured_context.maintenance_entries) == 1
    assert '"task": "Check gearbox for leaks"' in prompt
    assert '"task": "Check gearbox"' not in prompt
    assert '"page_start": 45' in prompt
    assert '"page_start": 46' in prompt
    assert '"section_path": "Preventive Maintenance > Gearbox"' in prompt
    assert '"section_path": "Preventive Maintenance > Lubrication"' in prompt
