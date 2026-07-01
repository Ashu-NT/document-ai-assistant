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


# ---------------------------------------------------------------------------
# Identifier persistence and lookup via value
# ---------------------------------------------------------------------------

def test_identifiers_populated_after_promotion_and_save(db_uow) -> None:
    """Ingest path: promote identifiers → save graph → query by part number."""
    document_id = "doc_prom_001"
    chunk_id = "chunk_prom_001"
    chunk = _make_chunk(chunk_id, document_id)
    graph = _make_graph(document_id, [chunk])

    spare = _make_spare_part("sp_001", document_id, "HP-001", chunk_id)
    result = _extraction_result(document_id, spare_parts=[spare])

    service = IdentifierPromotionService()
    identifiers = service.promote(
        extraction_result=result,
        document_graph=graph,
        id_generator=IdGenerator(),
    )
    assert len(identifiers) >= 1

    for identifier in identifiers:
        graph.identifiers[identifier.identifier_id] = identifier

    db_uow.documents.save_document_graph(graph)
    db_uow.commit()

    found = db_uow.documents.search_identifiers("HP-001")
    assert len(found) == 1
    assert found[0].identifier_type == IdentifierType.PART_NUMBER
    assert found[0].document_id == document_id


def test_identifier_normalized_value_enables_lookup(db_uow) -> None:
    """Normalized lookup matches raw value with extra whitespace."""
    document_id = "doc_norm_001"
    chunk_id = "chunk_norm_001"
    chunk = _make_chunk(chunk_id, document_id)
    graph = _make_graph(document_id, [chunk])

    spare = _make_spare_part("sp_002", document_id, " HP-002 ", chunk_id)
    result = _extraction_result(document_id, spare_parts=[spare])

    service = IdentifierPromotionService()
    identifiers = service.promote(
        extraction_result=result,
        document_graph=graph,
        id_generator=IdGenerator(),
    )
    for identifier in identifiers:
        graph.identifiers[identifier.identifier_id] = identifier

    db_uow.documents.save_document_graph(graph)
    db_uow.commit()

    found = db_uow.documents.search_identifiers("HP-002")
    assert len(found) == 1


# ---------------------------------------------------------------------------
# Type-filtered lookup
# ---------------------------------------------------------------------------

def test_search_identifiers_by_type_returns_correct_type(db_uow) -> None:
    document_id = "doc_type_001"
    chunk_id = "chunk_type_001"
    chunk = _make_chunk(chunk_id, document_id)
    graph = _make_graph(document_id, [chunk])

    spare = _make_spare_part("sp_003", document_id, "FLT-100", chunk_id)
    equipment = _make_equipment("eq_001", document_id, "HP-500", chunk_id)
    result = _extraction_result(document_id, spare_parts=[spare], equipment=[equipment])

    service = IdentifierPromotionService()
    identifiers = service.promote(
        extraction_result=result,
        document_graph=graph,
        id_generator=IdGenerator(),
    )
    for identifier in identifiers:
        graph.identifiers[identifier.identifier_id] = identifier

    db_uow.documents.save_document_graph(graph)
    db_uow.commit()

    part_numbers = db_uow.documents.search_identifiers_by_type(
        IdentifierType.PART_NUMBER.value, document_id,
    )
    model_numbers = db_uow.documents.search_identifiers_by_type(
        IdentifierType.MODEL_NUMBER.value, document_id,
    )

    assert all(i.identifier_type == IdentifierType.PART_NUMBER for i in part_numbers)
    assert all(i.identifier_type == IdentifierType.MODEL_NUMBER for i in model_numbers)
    assert len(part_numbers) >= 1
    assert len(model_numbers) >= 1


# ---------------------------------------------------------------------------
# Chunk-scoped lookup
# ---------------------------------------------------------------------------

def test_get_identifiers_for_chunk_scoped_correctly(db_uow) -> None:
    document_id = "doc_chunk_001"
    chunk_a = _make_chunk("chunk_a", document_id)
    chunk_b = _make_chunk("chunk_b", document_id, page_start=20, page_end=21)
    graph = _make_graph(document_id, [chunk_a, chunk_b])

    spare_a = _make_spare_part("sp_a", document_id, "PN-AAA", "chunk_a")
    spare_b = _make_spare_part("sp_b", document_id, "PN-BBB", "chunk_b")
    result = _extraction_result(document_id, spare_parts=[spare_a, spare_b])

    service = IdentifierPromotionService()
    identifiers = service.promote(
        extraction_result=result,
        document_graph=graph,
        id_generator=IdGenerator(),
    )
    for identifier in identifiers:
        graph.identifiers[identifier.identifier_id] = identifier

    db_uow.documents.save_document_graph(graph)
    db_uow.commit()

    for_a = db_uow.documents.get_identifiers_for_chunk("chunk_a")
    for_b = db_uow.documents.get_identifiers_for_chunk("chunk_b")

    assert all(i.chunk_id == "chunk_a" for i in for_a)
    assert all(i.chunk_id == "chunk_b" for i in for_b)
    assert len(for_a) >= 1
    assert len(for_b) >= 1


# ---------------------------------------------------------------------------
# Page-scoped lookup
# ---------------------------------------------------------------------------

def test_get_identifiers_on_page_returns_matching_identifiers(db_uow) -> None:
    document_id = "doc_page_001"
    chunk_p10 = _make_chunk("chunk_p10", document_id, page_start=10, page_end=12)
    chunk_p20 = _make_chunk("chunk_p20", document_id, page_start=20, page_end=22)
    graph = _make_graph(document_id, [chunk_p10, chunk_p20])

    spare_p10 = _make_spare_part("sp_p10", document_id, "PN-P10", "chunk_p10")
    spare_p20 = _make_spare_part("sp_p20", document_id, "PN-P20", "chunk_p20")
    result = _extraction_result(document_id, spare_parts=[spare_p10, spare_p20])

    service = IdentifierPromotionService()
    identifiers = service.promote(
        extraction_result=result,
        document_graph=graph,
        id_generator=IdGenerator(),
    )
    for identifier in identifiers:
        graph.identifiers[identifier.identifier_id] = identifier

    db_uow.documents.save_document_graph(graph)
    db_uow.commit()

    on_page_11 = db_uow.documents.get_identifiers_on_page(document_id, page=11)
    on_page_21 = db_uow.documents.get_identifiers_on_page(document_id, page=21)
    on_page_50 = db_uow.documents.get_identifiers_on_page(document_id, page=50)

    assert len(on_page_11) >= 1
    assert all(
        i.page_start is not None and i.page_start <= 11 for i in on_page_11
    )
    assert len(on_page_21) >= 1
    assert len(on_page_50) == 0


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
