"""Integration tests: identifier persistence → lookup by value, type, chunk, and page."""

from __future__ import annotations

import pytest

from src.application.services.document import IdentifierPromotionService

from src.domain.common import ChunkType, DocumentType, IdentifierType, SourceLocation

from src.domain.document import Document, DocumentChunk, DocumentGraph, DocumentHashes

from src.domain.extraction import EquipmentInfo, ExtractionResult, SparePart

from src.shared.ids import IdGenerator

def _make_document(document_id: str = "doc_001") -> Document:
    return Document(
        document_id=document_id,
        file_name="pump.pdf",
        file_path="data/pump.pdf",
        hashes=DocumentHashes(file_hash="fh1", content_hash="ch1"),
        document_type=DocumentType.MANUAL,
    )

def _make_chunk(
    chunk_id: str,
    document_id: str = "doc_001",
    page_start: int | None = 10,
    page_end: int | None = 12,
    section_id: str | None = "sec_001",
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        section_id=section_id,
        content="Replace filter HP-001 every 1000 hours.",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        sequence_number=1,
        chunk_index=0,
        chunk_total=1,
        source=SourceLocation(page_start=page_start, page_end=page_end),
    )

def _make_graph(
    document_id: str = "doc_001",
    chunks: list[DocumentChunk] | None = None,
) -> DocumentGraph:
    graph = DocumentGraph(document=_make_document(document_id))
    for chunk in (chunks or []):
        graph.add_chunk(chunk)
    return graph

def _make_spare_part(
    spare_part_id: str,
    document_id: str,
    part_number: str,
    chunk_id: str,
) -> SparePart:
    return SparePart(
        spare_part_id=spare_part_id,
        document_id=document_id,
        part_number=part_number,
        description="Hydraulic filter",
        quantity="1",
        source_chunk_id=chunk_id,
        confidence_score=0.95,
    )

def _make_equipment(
    equipment_id: str,
    document_id: str,
    model_number: str,
    chunk_id: str,
) -> EquipmentInfo:
    return EquipmentInfo(
        equipment_id=equipment_id,
        document_id=document_id,
        name="Hydraulic Pump",
        model_number=model_number,
        source_chunk_id=chunk_id,
        confidence_score=0.90,
    )

def _extraction_result(
    document_id: str,
    spare_parts: list[SparePart] | None = None,
    equipment: list[EquipmentInfo] | None = None,
) -> ExtractionResult:
    return ExtractionResult(
        extraction_id="ext_001",
        document_id=document_id,
        maintenance_tasks=[],
        spare_parts=spare_parts or [],
        equipment=equipment or [],
        manufacturers=[],
        confidence_score=0.88,
    )

def test_get_identifiers_on_page_excludes_other_documents(db_uow) -> None:
    doc_a = "doc_page_a"
    doc_b = "doc_page_b"

    chunk_a = DocumentChunk(
        chunk_id="ck_a",
        document_id=doc_a,
        section_id="sec_a",
        content="Part PN-AA",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        sequence_number=1,
        chunk_index=0,
        chunk_total=1,
        source=SourceLocation(page_start=5, page_end=5),
    )
    chunk_b = DocumentChunk(
        chunk_id="ck_b",
        document_id=doc_b,
        section_id="sec_b",
        content="Part PN-BB",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        sequence_number=1,
        chunk_index=0,
        chunk_total=1,
        source=SourceLocation(page_start=5, page_end=5),
    )
    graph_a = DocumentGraph(
        document=Document(
            document_id=doc_a,
            file_name="a.pdf",
            file_path="data/a.pdf",
            hashes=DocumentHashes(file_hash="fha", content_hash="cha"),
        )
    )
    graph_b = DocumentGraph(
        document=Document(
            document_id=doc_b,
            file_name="b.pdf",
            file_path="data/b.pdf",
            hashes=DocumentHashes(file_hash="fhb", content_hash="chb"),
        )
    )
    graph_a.add_chunk(chunk_a)
    graph_b.add_chunk(chunk_b)

    service = IdentifierPromotionService()
    id_gen = IdGenerator()
    for spare, graph in [
        (_make_spare_part("sp_aa", doc_a, "PN-AA", "ck_a"), graph_a),
        (_make_spare_part("sp_bb", doc_b, "PN-BB", "ck_b"), graph_b),
    ]:
        ids = service.promote(
            extraction_result=_extraction_result(graph.document.document_id, spare_parts=[spare]),
            document_graph=graph,
            id_generator=id_gen,
        )
        for identifier in ids:
            graph.identifiers[identifier.identifier_id] = identifier

    db_uow.documents.save_document_graph(graph_a)
    db_uow.documents.save_document_graph(graph_b)
    db_uow.commit()

    on_page_a = db_uow.documents.get_identifiers_on_page(doc_a, page=5)
    on_page_b = db_uow.documents.get_identifiers_on_page(doc_b, page=5)

    assert all(i.document_id == doc_a for i in on_page_a)
    assert all(i.document_id == doc_b for i in on_page_b)
