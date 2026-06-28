import pytest

from src.application.prompts.answer_generation import ANSWER_PROMPT_VERSION
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.answer_generation_service import (
    AnswerGenerationService,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


class FakeLLMService:
    def __init__(self, response: str = "The answer is 1000 hours.") -> None:
        self.response = response
        self.calls: list[dict] = []

    def generate(self, prompt: str, model: str | None = None) -> str:
        self.calls.append({"prompt": prompt, "model": model})
        return self.response


def _make_chunk(
    chunk_id: str = "chunk_001",
    document_id: str = "doc_001",
    content: str = "Replace hydraulic filter every 1000 operating hours.",
    citation: Citation | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path=["Maintenance Schedule"],
        source=SourceLocation(page_start=5, page_end=5),
        citation=citation,
    )


def _make_citation(chunk_id: str, document_id: str = "doc_001") -> Citation:
    return Citation(
        citation_id=f"cit_{chunk_id}",
        document_id=document_id,
        chunk_id=chunk_id,
    )


def make_service(
    llm: FakeLLMService | None = None,
    model: str = "qwen3:8b",
) -> tuple[AnswerGenerationService, FakeLLMService]:
    llm = llm or FakeLLMService()
    service = AnswerGenerationService(
        llm_service=llm,
        answer_generation_model=model,
    )
    return service, llm


# ---------------------------------------------------------------------------
# Test 1 — generate returns answer_text from LLM output
# ---------------------------------------------------------------------------


def test_generate_returns_llm_output_as_answer_text() -> None:
    service, llm = make_service()
    chunk = _make_chunk()
    request = AnswerGenerationRequest(
        question="When to replace the filter?",
        context_chunks=[chunk],
    )

    result = service.generate(request)

    assert result.answer_text == "The answer is 1000 hours."


# ---------------------------------------------------------------------------
# Test 2 — prompt_version is set from module constant
# ---------------------------------------------------------------------------


def test_generate_sets_prompt_version() -> None:
    service, _ = make_service()
    chunk = _make_chunk()
    request = AnswerGenerationRequest(
        question="Test question?",
        context_chunks=[chunk],
    )

    result = service.generate(request)

    assert result.prompt_version == ANSWER_PROMPT_VERSION


# ---------------------------------------------------------------------------
# Test 3 — citations are built from chunks that have a citation object
# ---------------------------------------------------------------------------


def test_generate_builds_citations_from_chunks_with_citation() -> None:
    citation = _make_citation("chunk_001")
    chunk_with_citation = _make_chunk(chunk_id="chunk_001", citation=citation)
    chunk_without_citation = _make_chunk(chunk_id="chunk_002", citation=None)

    service, _ = make_service()
    request = AnswerGenerationRequest(
        question="Test?",
        context_chunks=[chunk_with_citation, chunk_without_citation],
    )

    result = service.generate(request)

    assert len(result.citations) == 1
    assert result.citations[0] is citation
    assert result.cited_chunk_ids == ["chunk_001"]


# ---------------------------------------------------------------------------
# Test 4 — chunks without citations produce empty citations list
# ---------------------------------------------------------------------------


def test_generate_empty_citations_when_no_chunk_has_citation() -> None:
    chunks = [_make_chunk(chunk_id=f"c{i}", citation=None) for i in range(3)]
    service, _ = make_service()
    request = AnswerGenerationRequest(
        question="Any question?",
        context_chunks=chunks,
    )

    result = service.generate(request)

    assert result.citations == []
    assert result.cited_chunk_ids == []


# ---------------------------------------------------------------------------
# Test 5 — model_name is echoed into result and metadata
# ---------------------------------------------------------------------------


def test_generate_model_name_is_reflected_in_result_and_metadata() -> None:
    service, _ = make_service(model="qwen3:8b")
    chunk = _make_chunk()
    request = AnswerGenerationRequest(
        question="What is the pressure?",
        context_chunks=[chunk],
    )

    result = service.generate(request)

    assert result.model_name == "qwen3:8b"
    assert result.metadata is not None
    assert result.metadata.model_name == "qwen3:8b"
    assert result.metadata.model_type == "answer_generation"
    assert result.metadata.prompt_version == ANSWER_PROMPT_VERSION
