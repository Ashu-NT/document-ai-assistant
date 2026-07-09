import pytest

from src.application.prompts.extraction import ExtractionPromptType
from src.application.workflows.extraction.candidates.extraction_candidate_selector import (
    ExtractionCandidateSelector,
    _CHUNK_TYPE_CANDIDATES,
    _UNGATED_CHUNK_TYPES,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk


class FakeLLMRouter:
    def __init__(self, result: frozenset | None) -> None:
        self.result = result
        self.calls: list[DocumentChunk] = []

    def route(self, chunk: DocumentChunk):
        self.calls.append(chunk)
        return self.result


def test_every_chunk_type_is_deliberately_mapped_or_ungated() -> None:
    covered = set(_CHUNK_TYPE_CANDIDATES) | _UNGATED_CHUNK_TYPES
    assert covered == set(ChunkType)


@pytest.mark.parametrize("chunk_type", [ChunkType.GENERAL, ChunkType.UNKNOWN])
def test_ungated_chunk_types_return_every_candidate(chunk_type) -> None:
    selector = ExtractionCandidateSelector()

    result = selector.select(chunk_type)

    assert result == frozenset(ExtractionPromptType)


def test_identifier_is_always_a_candidate_for_gated_types() -> None:
    selector = ExtractionCandidateSelector()

    for chunk_type in _CHUNK_TYPE_CANDIDATES:
        assert ExtractionPromptType.IDENTIFIER in selector.select(chunk_type)


def test_maintenance_interval_maps_to_maintenance_task_and_interval() -> None:
    selector = ExtractionCandidateSelector()

    result = selector.select(ChunkType.MAINTENANCE_INTERVAL)

    assert result == frozenset(
        {
            ExtractionPromptType.MAINTENANCE_TASK,
            ExtractionPromptType.MAINTENANCE_INTERVAL,
            ExtractionPromptType.IDENTIFIER,
        }
    )


def test_safety_warning_maps_to_only_safety_warning_and_identifier() -> None:
    selector = ExtractionCandidateSelector()

    result = selector.select(ChunkType.SAFETY_WARNING)

    assert result == frozenset(
        {ExtractionPromptType.SAFETY_WARNING, ExtractionPromptType.IDENTIFIER}
    )


def test_spare_parts_table_includes_manufacturer_and_supplier() -> None:
    selector = ExtractionCandidateSelector()

    result = selector.select(ChunkType.SPARE_PARTS_TABLE)

    assert result == frozenset(
        {
            ExtractionPromptType.SPARE_PART,
            ExtractionPromptType.MANUFACTURER,
            ExtractionPromptType.SUPPLIER,
            ExtractionPromptType.EQUIPMENT,
            ExtractionPromptType.IDENTIFIER,
        }
    )


def test_overview_includes_contact_point_candidates() -> None:
    selector = ExtractionCandidateSelector()

    result = selector.select(ChunkType.OVERVIEW)

    assert result == frozenset(
        {
            ExtractionPromptType.EQUIPMENT,
            ExtractionPromptType.MANUFACTURER,
            ExtractionPromptType.SUPPLIER,
            ExtractionPromptType.CONTACT_POINT,
            ExtractionPromptType.IDENTIFIER,
        }
    )


def test_certification_info_narrows_to_identifier_only() -> None:
    selector = ExtractionCandidateSelector()

    result = selector.select(ChunkType.CERTIFICATION_INFO)

    assert result == frozenset({ExtractionPromptType.IDENTIFIER})


def test_drawing_reference_narrows_to_identifier_only() -> None:
    selector = ExtractionCandidateSelector()

    result = selector.select(ChunkType.DRAWING_REFERENCE)

    assert result == frozenset({ExtractionPromptType.IDENTIFIER})


def test_select_for_chunk_reads_chunk_type_off_the_chunk() -> None:
    selector = ExtractionCandidateSelector()
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id="document_001",
        section_id="section_001",
        content="Depressurize before servicing.",
        chunk_type=ChunkType.SAFETY_WARNING,
        source=SourceLocation(),
    )

    result = selector.select_for_chunk(chunk)

    assert result == selector.select(ChunkType.SAFETY_WARNING)


def test_all_types_returns_every_extraction_prompt_type() -> None:
    assert ExtractionCandidateSelector.all_types() == frozenset(ExtractionPromptType)


def test_select_for_chunk_includes_cross_signals_beyond_chunk_type() -> None:
    selector = ExtractionCandidateSelector()
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id="document_001",
        section_id="section_001",
        content="Manufactured by Acme Hydraulics GmbH.",
        chunk_type=ChunkType.SAFETY_WARNING,
        source=SourceLocation(),
    )

    result = selector.select_for_chunk(chunk)

    assert ExtractionPromptType.SAFETY_WARNING in result
    assert ExtractionPromptType.MANUFACTURER in result


def test_select_for_chunk_uses_llm_router_result_for_general_chunks() -> None:
    router = FakeLLMRouter(frozenset({ExtractionPromptType.PROCEDURE}))
    selector = ExtractionCandidateSelector(llm_router=router)
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id="document_001",
        section_id="section_001",
        content="Ambiguous content.",
        chunk_type=ChunkType.GENERAL,
        source=SourceLocation(),
    )

    result = selector.select_for_chunk(chunk)

    assert result == frozenset(
        {ExtractionPromptType.PROCEDURE, ExtractionPromptType.IDENTIFIER}
    )
    assert router.calls == [chunk]


def test_select_for_chunk_falls_open_when_router_returns_none() -> None:
    router = FakeLLMRouter(None)
    selector = ExtractionCandidateSelector(llm_router=router)
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id="document_001",
        section_id="section_001",
        content="Ambiguous content.",
        chunk_type=ChunkType.UNKNOWN,
        source=SourceLocation(),
    )

    result = selector.select_for_chunk(chunk)

    assert result == frozenset(ExtractionPromptType)


def test_select_for_chunk_falls_open_when_no_router_configured() -> None:
    selector = ExtractionCandidateSelector()
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id="document_001",
        section_id="section_001",
        content="Ambiguous content.",
        chunk_type=ChunkType.GENERAL,
        source=SourceLocation(),
    )

    result = selector.select_for_chunk(chunk)

    assert result == frozenset(ExtractionPromptType)


def test_select_for_chunk_router_is_not_consulted_for_resolved_chunk_types() -> None:
    router = FakeLLMRouter(frozenset({ExtractionPromptType.PROCEDURE}))
    selector = ExtractionCandidateSelector(llm_router=router)
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id="document_001",
        section_id="section_001",
        content="Depressurize before servicing.",
        chunk_type=ChunkType.SAFETY_WARNING,
        source=SourceLocation(),
    )

    selector.select_for_chunk(chunk)

    assert router.calls == []
