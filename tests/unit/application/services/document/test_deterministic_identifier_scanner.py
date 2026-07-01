from __future__ import annotations

import pytest

from src.application.services.document.deterministic_identifier_scanner import (
    DeterministicIdentifierScanner,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.common.enums import IdentifierType
from src.domain.document import Document, DocumentChunk, DocumentGraph
from src.domain.document.value_objects import DocumentHashes
from src.shared.ids import IdGenerator


def _make_document(document_id: str = "doc_001") -> Document:
    return Document(
        document_id=document_id,
        file_name="pump.pdf",
        file_path="data/pump.pdf",
        hashes=DocumentHashes(file_hash="fh", content_hash="ch"),
    )


def _make_chunk(
    chunk_id: str = "chunk_001",
    content: str = "",
    document_id: str = "doc_001",
    page_start: int | None = None,
    page_end: int | None = None,
    section_id: str | None = "sec_001",
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        section_id=section_id,
        content=content,
        chunk_type=ChunkType.GENERAL,
        sequence_number=1,
        chunk_index=0,
        chunk_total=1,
        source=SourceLocation(page_start=page_start, page_end=page_end),
    )


def _make_graph(
    chunks: list[DocumentChunk] | None = None,
    document_id: str = "doc_001",
) -> DocumentGraph:
    graph = DocumentGraph(document=_make_document(document_id))
    for chunk in (chunks or []):
        graph.add_chunk(chunk)
    return graph


def _scanner() -> DeterministicIdentifierScanner:
    return DeterministicIdentifierScanner()


# --- drawing number tests ---

def test_scans_drawing_number_drg_pattern():
    graph = _make_graph([_make_chunk(content="See drawing DRG-1234 for details.")])
    results = _scanner().scan(graph, IdGenerator())
    assert len(results) == 1
    assert results[0].identifier_type == IdentifierType.DRAWING_NUMBER
    assert "DRG-1234" in results[0].raw_value.upper() or "DRG" in results[0].raw_value.upper()


def test_scans_drawing_number_dwg_pattern():
    graph = _make_graph([_make_chunk(content="Refer to DWG 500 for assembly.")])
    results = _scanner().scan(graph, IdGenerator())
    assert len(results) == 1
    assert results[0].identifier_type == IdentifierType.DRAWING_NUMBER


def test_scans_cert_number_iso_pattern():
    graph = _make_graph([_make_chunk(content="Certified to ISO 9001 standards.")])
    results = _scanner().scan(graph, IdGenerator())
    assert len(results) == 1
    assert results[0].identifier_type == IdentifierType.COMPONENT_CODE


def test_scans_cert_number_iec_pattern():
    graph = _make_graph([_make_chunk(content="Compliant with IEC 61508 safety.")])
    results = _scanner().scan(graph, IdGenerator())
    assert len(results) == 1
    assert results[0].identifier_type == IdentifierType.COMPONENT_CODE


def test_deduplication_across_chunks():
    graph = _make_graph([
        _make_chunk("chunk_001", content="See DRG-1234."),
        _make_chunk("chunk_002", content="Also refer to DRG-1234."),
    ])
    results = _scanner().scan(graph, IdGenerator())
    assert len(results) == 1


def test_deduplication_respects_existing_normalized():
    graph = _make_graph([_make_chunk(content="See DRG-1234.")])
    existing = {("DRG-1234", IdentifierType.DRAWING_NUMBER.value)}
    results = _scanner().scan(graph, IdGenerator(), existing_normalized=existing)
    assert results == []


def test_multiple_patterns_in_same_chunk():
    graph = _make_graph([_make_chunk(content="Ref DRG-1234 and ISO 9001.")])
    results = _scanner().scan(graph, IdGenerator())
    assert len(results) == 2
    types = {r.identifier_type for r in results}
    assert IdentifierType.DRAWING_NUMBER in types
    assert IdentifierType.COMPONENT_CODE in types


def test_chunk_metadata_attached_to_identifier():
    chunk = _make_chunk(
        chunk_id="chunk_001",
        content="See DRG-1234.",
        page_start=5,
        page_end=6,
        section_id="sec_abc",
    )
    graph = _make_graph([chunk])
    results = _scanner().scan(graph, IdGenerator())
    assert len(results) == 1
    result = results[0]
    assert result.chunk_id == "chunk_001"
    assert result.section_id == "sec_abc"
    assert result.page_start == 5
    assert result.page_end == 6


def test_document_id_from_graph():
    graph = _make_graph([_make_chunk(content="DRG-999.")], document_id="doc_XYZ")
    results = _scanner().scan(graph, IdGenerator())
    assert len(results) == 1
    assert results[0].document_id == "doc_XYZ"


def test_empty_graph_produces_no_identifiers():
    graph = _make_graph([])
    results = _scanner().scan(graph, IdGenerator())
    assert results == []


def test_no_pattern_match_produces_no_identifiers():
    graph = _make_graph([_make_chunk(content="This is a general text with no identifiers.")])
    results = _scanner().scan(graph, IdGenerator())
    assert results == []


def test_identifier_ids_are_unique():
    graph = _make_graph([
        _make_chunk("c1", content="DRG-001"),
        _make_chunk("c2", content="DRG-002"),
    ])
    results = _scanner().scan(graph, IdGenerator())
    ids = [r.identifier_id for r in results]
    assert len(ids) == len(set(ids))
