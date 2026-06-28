from src.application.prompts.answer_generation import (
    ANSWER_PROMPT_VERSION,
    AnswerPromptBuilder,
)
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _make_chunk(
    chunk_id: str = "chunk_001",
    document_id: str = "doc_001",
    content: str = "Hydraulic filter must be replaced every 1000 hours.",
    section_path: list[str] | None = None,
    page_start: int | None = 5,
    page_end: int | None = 5,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path=section_path or ["Maintenance Schedule"],
        source=SourceLocation(page_start=page_start, page_end=page_end),
    )


def test_answer_prompt_builder_produces_grounding_instructions() -> None:
    builder = AnswerPromptBuilder()
    request = AnswerGenerationRequest(
        question="When should I replace the hydraulic filter?",
        context_chunks=[_make_chunk()],
    )

    prompt = builder.build(request)

    assert builder.prompt_version == ANSWER_PROMPT_VERSION
    assert "ONLY the provided sources" in prompt
    assert "Do not use outside knowledge" in prompt
    assert "Question: When should I replace the hydraulic filter?" in prompt


def test_answer_prompt_builder_includes_provided_sources() -> None:
    builder = AnswerPromptBuilder()
    request = AnswerGenerationRequest(
        question="Test?",
        context_chunks=[
            _make_chunk(chunk_id="c1", content="Content A"),
            _make_chunk(chunk_id="c2", content="Content B"),
        ],
    )

    prompt = builder.build(request)

    assert "SOURCE 1" in prompt
    assert "SOURCE 2" in prompt
    assert "Content A" in prompt
    assert "Content B" in prompt
    assert "Document: doc_001" in prompt
    assert "Section: Maintenance Schedule" in prompt


def test_answer_prompt_builder_formats_page_ranges() -> None:
    same_page_chunk = _make_chunk(page_start=7, page_end=7)
    page_span_chunk = _make_chunk(page_start=3, page_end=6)
    unknown_page_chunk = _make_chunk(page_start=None, page_end=None)

    assert AnswerPromptBuilder._format_page_range(same_page_chunk) == "7"
    assert AnswerPromptBuilder._format_page_range(page_span_chunk) == "3-6"
    assert AnswerPromptBuilder._format_page_range(unknown_page_chunk) == "N/A"
