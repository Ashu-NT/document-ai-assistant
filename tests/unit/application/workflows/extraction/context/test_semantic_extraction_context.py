from src.application.workflows.extraction.context.semantic_extraction_context import (
    SemanticExtractionContext,
)
from src.domain.common import SourceLocation
from src.domain.document import DocumentChunk, DocumentSection


def make_chunk(**overrides) -> DocumentChunk:
    defaults = dict(
        chunk_id="chunk_001",
        document_id="document_001",
        section_id="section_001",
        content="Replace hydraulic filter every 1000 operating hours.",
        section_path=["4", "Maintenance"],
        element_ids=["el_001"],
        table_ids=["table_001"],
        source=SourceLocation(page_start=4, page_end=5),
        chunk_index=1,
    )
    defaults.update(overrides)
    return DocumentChunk(**defaults)


def test_properties_read_from_chunk_when_no_section() -> None:
    chunk = make_chunk()
    context = SemanticExtractionContext(document_id="document_001", chunk=chunk)

    assert context.chunk_id == "chunk_001"
    assert context.section_id == "section_001"
    assert context.section_path == ("4", "Maintenance")
    assert context.page_start == 4
    assert context.page_end == 5
    assert context.table_id == "table_001"
    assert context.source_element_ids == ("el_001",)
    assert context.parent_section_id is None


def test_parent_section_id_comes_from_section() -> None:
    chunk = make_chunk()
    section = DocumentSection(
        section_id="section_001",
        document_id="document_001",
        title="Maintenance",
        parent_section_id="section_root",
    )
    context = SemanticExtractionContext(
        document_id="document_001", chunk=chunk, section=section
    )

    assert context.parent_section_id == "section_root"


def test_table_id_is_none_when_chunk_has_no_tables() -> None:
    chunk = make_chunk(table_ids=[])
    context = SemanticExtractionContext(document_id="document_001", chunk=chunk)

    assert context.table_id is None


def test_to_source_metadata_carries_nearby_chunk_ids() -> None:
    chunk = make_chunk()
    context = SemanticExtractionContext(
        document_id="document_001",
        chunk=chunk,
        nearby_chunk_ids=("chunk_000", "chunk_002"),
    )

    metadata = context.to_source_metadata()

    assert metadata.document_id == "document_001"
    assert metadata.chunk_id == "chunk_001"
    assert metadata.section_id == "section_001"
    assert metadata.section_path == ("4", "Maintenance")
    assert metadata.page_start == 4
    assert metadata.page_end == 5
    assert metadata.table_id == "table_001"
    assert metadata.source_element_ids == ("el_001",)
    assert metadata.nearby_chunk_ids == ("chunk_000", "chunk_002")
