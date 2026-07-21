from src.application.workflows.question_answering.answer_pipeline.retrieved_chunk_converter import (
    to_retrieved_chunk,
)
from src.domain.common import SourceLocation
from src.domain.document.entities.chunk import DocumentChunk


def _document_chunk(**overrides) -> DocumentChunk:
    defaults = dict(
        chunk_id="chunk_001",
        document_id="doc_001",
        section_id="sec_001",
        content="ACME Corp, https://acme.example",
        section_path=["Manufacturer", "Contact Details"],
        source=SourceLocation(page_start=4, page_end=4),
        sequence_number=7,
    )
    defaults.update(overrides)
    return DocumentChunk(**defaults)


def test_to_retrieved_chunk_builds_a_real_citation() -> None:
    chunk = to_retrieved_chunk(_document_chunk())

    assert chunk.citation is not None
    assert chunk.citation.chunk_id == "chunk_001"
    assert chunk.citation.document_id == "doc_001"
    assert chunk.citation.section_id == "sec_001"
    assert chunk.citation.section_title == "Contact Details"
    assert chunk.citation.source.page_start == 4


def test_to_retrieved_chunk_citation_has_no_section_title_without_a_section_path() -> None:
    chunk = to_retrieved_chunk(_document_chunk(section_path=[]))

    assert chunk.citation is not None
    assert chunk.citation.section_title is None


def test_to_retrieved_chunk_preserves_core_fields() -> None:
    chunk = to_retrieved_chunk(_document_chunk())

    assert chunk.chunk_id == "chunk_001"
    assert chunk.document_id == "doc_001"
    assert chunk.content == "ACME Corp, https://acme.example"
    assert chunk.retrieval_source == "structured_lookup"
    assert chunk.metadata["sequence_number"] == "7"
