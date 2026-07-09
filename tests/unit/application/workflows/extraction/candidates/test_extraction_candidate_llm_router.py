import json

from src.application.prompts.extraction import ExtractionPromptType
from src.application.workflows.extraction.candidates.extraction_candidate_llm_router import (
    ExtractionCandidateLLMRouter,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk


class FakeLLMService:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[dict] = []

    def generate(self, prompt, model=None, response_schema=None):
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "response_schema": response_schema,
            }
        )
        return self.response


def make_chunk(content: str = "Ambiguous content.") -> DocumentChunk:
    return DocumentChunk(
        chunk_id="chunk_001",
        document_id="document_001",
        section_id="section_001",
        content=content,
        chunk_type=ChunkType.GENERAL,
        source=SourceLocation(),
    )


def test_route_returns_none_when_disabled() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService(json.dumps({"candidate_types": ["safety_warning"]})),
        enabled=False,
    )

    assert router.route(make_chunk()) is None


def test_route_returns_none_when_no_llm_service() -> None:
    router = ExtractionCandidateLLMRouter(llm_service=None, enabled=True)

    assert router.route(make_chunk()) is None


def test_route_returns_none_for_empty_content() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService(json.dumps({"candidate_types": ["safety_warning"]})),
        enabled=True,
    )

    assert router.route(make_chunk(content="   ")) is None


def test_route_resolves_candidate_types() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService(
            json.dumps({"candidate_types": ["safety_warning", "spare_part"]})
        ),
        enabled=True,
    )

    result = router.route(make_chunk())

    assert result == frozenset(
        {ExtractionPromptType.SAFETY_WARNING, ExtractionPromptType.SPARE_PART}
    )
    assert isinstance(router._llm_service.calls[0]["response_schema"], dict)


def test_route_normalizes_casing_and_separators() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService(
            json.dumps(
                {"candidate_types": ["Safety Warning", "Spare-Part", "Contact Point"]}
            )
        ),
        enabled=True,
    )

    result = router.route(make_chunk())

    assert result == frozenset(
        {
            ExtractionPromptType.SAFETY_WARNING,
            ExtractionPromptType.SPARE_PART,
            ExtractionPromptType.CONTACT_POINT,
        }
    )


def test_route_drops_unrecognized_types() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService(
            json.dumps({"candidate_types": ["safety_warning", "not_a_real_type"]})
        ),
        enabled=True,
    )

    result = router.route(make_chunk())

    assert result == frozenset({ExtractionPromptType.SAFETY_WARNING})


def test_route_returns_none_for_empty_candidate_list() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService(json.dumps({"candidate_types": []})),
        enabled=True,
    )

    assert router.route(make_chunk()) is None


def test_route_returns_none_for_malformed_response() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService("not json at all"),
        enabled=True,
    )

    assert router.route(make_chunk()) is None


def test_route_passes_response_schema_to_llm() -> None:
    llm_service = FakeLLMService(json.dumps({"candidate_types": ["identifier"]}))
    router = ExtractionCandidateLLMRouter(
        llm_service=llm_service,
        enabled=True,
    )

    router.route(make_chunk())

    assert llm_service.calls
    assert isinstance(llm_service.calls[0]["response_schema"], dict)
    assert "candidate_types" in llm_service.calls[0]["response_schema"].get(
        "properties",
        {},
    )


def test_is_available_requires_both_enabled_and_llm_service() -> None:
    assert ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService("{}"), enabled=True
    ).is_available() is True
    assert ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService("{}"), enabled=False
    ).is_available() is False
    assert ExtractionCandidateLLMRouter(
        llm_service=None, enabled=True
    ).is_available() is False
