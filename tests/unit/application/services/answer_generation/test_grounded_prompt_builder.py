from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.grounded_prompt_builder import (
    GroundedPromptBuilder,
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


# ---------------------------------------------------------------------------
# Test 1 — prompt contains grounding rules
# ---------------------------------------------------------------------------


def test_prompt_contains_grounding_rules() -> None:
    builder = GroundedPromptBuilder()
    chunk = _make_chunk()
    request = AnswerGenerationRequest(
        question="When should I replace the hydraulic filter?",
        context_chunks=[chunk],
    )

    prompt = builder.build(request)

    assert "ONLY the provided sources" in prompt
    assert "Do not use outside knowledge" in prompt


# ---------------------------------------------------------------------------
# Test 2 — each chunk is emitted as a numbered SOURCE block
# ---------------------------------------------------------------------------


def test_prompt_emits_numbered_source_blocks() -> None:
    builder = GroundedPromptBuilder()
    chunks = [
        _make_chunk(chunk_id="c1", content="Content A"),
        _make_chunk(chunk_id="c2", content="Content B"),
    ]
    request = AnswerGenerationRequest(
        question="Test?",
        context_chunks=chunks,
    )

    prompt = builder.build(request)

    assert "SOURCE 1" in prompt
    assert "SOURCE 2" in prompt
    assert "Content A" in prompt
    assert "Content B" in prompt


# ---------------------------------------------------------------------------
# Test 3 — page range formatting handles same-page, range, and None
# ---------------------------------------------------------------------------


def test_page_range_same_page() -> None:
    chunk = _make_chunk(page_start=7, page_end=7)
    assert GroundedPromptBuilder._format_page_range(chunk) == "7"


def test_page_range_span() -> None:
    chunk = _make_chunk(page_start=3, page_end=6)
    assert GroundedPromptBuilder._format_page_range(chunk) == "3-6"


def test_page_range_none() -> None:
    chunk = _make_chunk(page_start=None, page_end=None)
    assert GroundedPromptBuilder._format_page_range(chunk) == "N/A"


# ---------------------------------------------------------------------------
# Test 4 — query_intent is included when set
# ---------------------------------------------------------------------------


def test_prompt_includes_query_intent_when_set() -> None:
    builder = GroundedPromptBuilder()
    chunk = _make_chunk()
    request = AnswerGenerationRequest(
        question="How often to replace the filter?",
        context_chunks=[chunk],
        query_intent="maintenance_interval",
    )

    prompt = builder.build(request)

    assert "maintenance_interval" in prompt


# ---------------------------------------------------------------------------
# Test 5 — max_context_chunks truncates sources
# ---------------------------------------------------------------------------


def test_prompt_respects_max_context_chunks() -> None:
    builder = GroundedPromptBuilder()
    chunks = [_make_chunk(chunk_id=f"c{i}", content=f"Content {i}") for i in range(5)]
    request = AnswerGenerationRequest(
        question="Test?",
        context_chunks=chunks,
        max_context_chunks=2,
    )

    prompt = builder.build(request)

    assert "Content 0" in prompt
    assert "Content 1" in prompt
    assert "Content 2" not in prompt
    assert "Content 4" not in prompt
