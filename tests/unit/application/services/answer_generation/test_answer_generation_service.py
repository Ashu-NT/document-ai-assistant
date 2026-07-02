import pytest

from src.application.prompts.answer_generation import ANSWER_PROMPT_VERSION
from src.application.services.answer_generation import AnswerIntent
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.answer_generation_service import (
    AnswerGenerationService,
)
from src.domain.common import ChunkType, IdentifierType
from src.domain.document.entities.identifier import Identifier
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


class FakePromptBuilder:
    prompt_version = ANSWER_PROMPT_VERSION

    def __init__(self) -> None:
        self.requests: list[AnswerGenerationRequest] = []

    def build(self, request: AnswerGenerationRequest) -> str:
        self.requests.append(request)
        return "PROMPT"


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


def test_generate_infers_answer_intent_when_missing() -> None:
    service, _ = make_service()
    request = AnswerGenerationRequest(
        question="specification",
        context_chunks=[
            _make_chunk(
                content="Test pressure: 700 bar\nDesign pressure: 350 bar\nSize: DN 8",
            )
        ],
    )

    result = service.generate(request)

    assert result.answer_intent == AnswerIntent.SPECIFICATION_SUMMARY
    assert result.diagnostics["answer_intent"] == "specification_summary"


def test_generate_builds_structured_context_and_format_policy_before_prompt() -> None:
    llm = FakeLLMService()
    prompt_builder = FakePromptBuilder()
    service = AnswerGenerationService(
        llm_service=llm,
        prompt_builder=prompt_builder,
        answer_generation_model="qwen3:8b",
    )
    request = AnswerGenerationRequest(
        question="specification",
        context_chunks=[
            _make_chunk(
                content="Test pressure: 700 bar\nDesign pressure: 350 bar",
                chunk_id="chunk_101",
            )
        ],
    )

    service.generate(request)

    built_request = prompt_builder.requests[0]
    assert built_request.answer_intent == AnswerIntent.SPECIFICATION_SUMMARY
    assert built_request.structured_context is not None
    assert built_request.structured_context.key_values
    assert built_request.format_policy is not None
    assert built_request.format_policy.preferred_format == "structured_bullets"


def test_generate_uses_maintenance_summary_path_and_reports_diagnostics() -> None:
    llm = FakeLLMService(response="Maintenance Tasks")
    prompt_builder = FakePromptBuilder()
    service = AnswerGenerationService(
        llm_service=llm,
        prompt_builder=prompt_builder,
        answer_generation_model="qwen3:8b",
    )
    request = AnswerGenerationRequest(
        question="What are maintenance tasks in the document?",
        context_chunks=[
            _make_chunk(
                content=(
                    "Replace cartridge filters every 1000 operating hours.\n"
                    "Inspect regulating valves."
                ),
                chunk_id="chunk_maintenance",
            )
        ],
    )

    result = service.generate(request)

    built_request = prompt_builder.requests[0]
    assert built_request.answer_intent == AnswerIntent.MAINTENANCE_SUMMARY
    assert built_request.structured_context is not None
    assert len(built_request.structured_context.maintenance_entries) == 2
    assert built_request.format_policy is not None
    assert built_request.format_policy.preferred_format == "maintenance_numbered_entries"
    assert result.diagnostics["answer_intent"] == "maintenance_summary"
    assert result.diagnostics["maintenance_items_found"] == 2
    assert result.diagnostics["maintenance_items_with_interval"] == 1
    assert result.diagnostics["maintenance_items_without_interval"] == 1
    assert result.diagnostics["maintenance_items_merged"] == 0


def test_generate_merges_duplicate_maintenance_entries_before_prompt_building() -> None:
    llm = FakeLLMService(response="Maintenance Tasks")
    prompt_builder = FakePromptBuilder()
    service = AnswerGenerationService(
        llm_service=llm,
        prompt_builder=prompt_builder,
        answer_generation_model="qwen3:8b",
    )
    request = AnswerGenerationRequest(
        question="What are the maintenance tasks in the document?",
        context_chunks=[
            _make_chunk(
                content="Check gearbox every 6 months.",
                chunk_id="chunk_a",
            ),
            _make_chunk(
                content="Check gearbox for leaks every 6 months.",
                chunk_id="chunk_b",
            ),
        ],
    )

    result = service.generate(request)

    built_request = prompt_builder.requests[0]
    assert built_request.structured_context is not None
    assert len(built_request.structured_context.maintenance_entries) == 1
    assert built_request.structured_context.maintenance_entries[0].task == (
        "Check gearbox for leaks"
    )
    assert result.diagnostics["maintenance_items_found"] == 1
    assert result.diagnostics["maintenance_items_merged"] == 1


def test_generate_uses_deterministic_identifier_renderer_and_skips_llm() -> None:
    llm = FakeLLMService(response="This answer should not be used.")
    service = AnswerGenerationService(
        llm_service=llm,
        answer_generation_model="qwen3:8b",
    )
    request = AnswerGenerationRequest(
        question="list all serial and part nmubers",
        context_chunks=[_make_chunk()],
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        resolved_identifiers=[
            Identifier(
                identifier_id="id_part",
                document_id="doc_001",
                raw_value="PN-001",
                identifier_type=IdentifierType.PART_NUMBER,
            ),
            Identifier(
                identifier_id="id_serial",
                document_id="doc_001",
                raw_value="SN-9001",
                identifier_type=IdentifierType.SERIAL_NUMBER,
            ),
        ],
    )

    result = service.generate(request)

    assert "Requested identifiers" in result.answer_text
    assert "Part Numbers:" in result.answer_text
    assert "- PN-001" in result.answer_text
    assert "Serial Numbers:" in result.answer_text
    assert "- SN-9001" in result.answer_text
    assert result.model_name == "deterministic_identifier_renderer"
    assert llm.calls == []
