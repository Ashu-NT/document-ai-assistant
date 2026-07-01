from __future__ import annotations

import pytest

from src.application.services.document.identifier_promotion_service import (
    IdentifierPromotionService,
)
from src.domain.common.enums import IdentifierType
from src.domain.document import Document, DocumentChunk, DocumentGraph
from src.domain.document.value_objects import DocumentHashes
from src.domain.common import ChunkType, DocumentType, SourceLocation
from src.domain.extraction.equipment_info import EquipmentInfo
from src.domain.extraction.extraction_result import ExtractionResult
from src.domain.extraction.spare_part import SparePart
from src.shared.ids import IdGenerator


# --- helpers ------------------------------------------------------------------

def _make_document(document_id: str = "doc_001") -> Document:
    return Document(
        document_id=document_id,
        file_name="pump.pdf",
        file_path="data/pump.pdf",
        hashes=DocumentHashes(file_hash="fh", content_hash="ch"),
    )


def _make_chunk(chunk_id: str = "chunk_001", document_id: str = "doc_001") -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        section_id="sec_001",
        content="Hydraulic filter HP-001",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        sequence_number=1,
        chunk_index=0,
        chunk_total=1,
        source=SourceLocation(),
    )


def _make_graph(
    document_id: str = "doc_001",
    chunk_ids: list[str] | None = None,
) -> DocumentGraph:
    graph = DocumentGraph(document=_make_document(document_id))
    for cid in (chunk_ids or ["chunk_001"]):
        graph.add_chunk(_make_chunk(cid, document_id))
    return graph


def _make_spare_part(
    part_number: str = "HP-001",
    document_id: str = "doc_001",
    source_chunk_id: str | None = "chunk_001",
    confidence_score: float | None = 0.9,
) -> SparePart:
    return SparePart(
        spare_part_id="spare_001",
        document_id=document_id,
        part_number=part_number,
        source_chunk_id=source_chunk_id,
        confidence_score=confidence_score,
    )


def _make_equipment(
    model_number: str | None = "HP-500",
    serial_number: str | None = None,
    document_id: str = "doc_001",
    source_chunk_id: str | None = "chunk_001",
    confidence_score: float | None = 0.85,
) -> EquipmentInfo:
    return EquipmentInfo(
        equipment_id="equip_001",
        document_id=document_id,
        model_number=model_number,
        serial_number=serial_number,
        source_chunk_id=source_chunk_id,
        confidence_score=confidence_score,
    )


def _make_extraction(
    spare_parts: list[SparePart] | None = None,
    equipment: list[EquipmentInfo] | None = None,
    document_id: str = "doc_001",
) -> ExtractionResult:
    return ExtractionResult(
        extraction_id="extraction_001",
        document_id=document_id,
        spare_parts=spare_parts or [],
        equipment=equipment or [],
    )


def _service() -> IdentifierPromotionService:
    return IdentifierPromotionService()


# --- tests -------------------------------------------------------------------

def test_promote_part_number_creates_identifier():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part("HP-001")])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    id_ = identifiers[0]
    assert id_.identifier_type == IdentifierType.PART_NUMBER
    assert id_.raw_value == "HP-001"
    assert id_.normalized_value == "HP-001"
    assert id_.document_id == "doc_001"
    assert id_.chunk_id == "chunk_001"
    assert id_.confidence_score == 0.9


def test_promote_model_number_creates_identifier():
    graph = _make_graph()
    extraction = _make_extraction(equipment=[_make_equipment(model_number="HP-500")])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].identifier_type == IdentifierType.MODEL_NUMBER
    assert identifiers[0].raw_value == "HP-500"


def test_promote_serial_number_creates_identifier():
    graph = _make_graph()
    extraction = _make_extraction(equipment=[_make_equipment(model_number=None, serial_number="SN-1234")])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].identifier_type == IdentifierType.SERIAL_NUMBER
    assert identifiers[0].raw_value == "SN-1234"


def test_promote_equipment_with_both_numbers_creates_two_identifiers():
    graph = _make_graph()
    extraction = _make_extraction(
        equipment=[_make_equipment(model_number="HP-500", serial_number="SN-1234")]
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 2
    types = {i.identifier_type for i in identifiers}
    assert types == {IdentifierType.MODEL_NUMBER, IdentifierType.SERIAL_NUMBER}


def test_deduplication_skips_same_normalized_value_and_type():
    graph = _make_graph(chunk_ids=["chunk_001", "chunk_002"])
    extraction = _make_extraction(
        spare_parts=[
            _make_spare_part("HP-001", source_chunk_id="chunk_001"),
            _make_spare_part("hp-001", source_chunk_id="chunk_002"),  # same after normalize
        ]
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].raw_value == "HP-001"


def test_deduplication_keeps_same_value_different_type():
    graph = _make_graph()
    extraction = _make_extraction(
        spare_parts=[_make_spare_part("HP-001")],
        equipment=[_make_equipment(model_number="HP-001")],
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 2
    types = {i.identifier_type for i in identifiers}
    assert IdentifierType.PART_NUMBER in types
    assert IdentifierType.MODEL_NUMBER in types


def test_invalid_chunk_id_not_attached():
    graph = _make_graph(chunk_ids=["chunk_001"])
    extraction = _make_extraction(
        spare_parts=[_make_spare_part("HP-001", source_chunk_id="chunk_unknown")]
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].chunk_id is None


def test_no_source_chunk_id_produces_null_chunk_id():
    graph = _make_graph()
    extraction = _make_extraction(
        spare_parts=[_make_spare_part("HP-001", source_chunk_id=None)]
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].chunk_id is None


def test_blank_part_number_skipped():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part("   ")])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []


def test_none_part_number_skipped():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part(None)])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []


def test_none_model_number_skipped():
    graph = _make_graph()
    extraction = _make_extraction(equipment=[_make_equipment(model_number=None)])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []


def test_empty_extraction_produces_no_identifiers():
    graph = _make_graph()
    extraction = _make_extraction()
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []


def test_identifier_ids_are_unique():
    graph = _make_graph(chunk_ids=["chunk_001", "chunk_002"])
    extraction = _make_extraction(
        spare_parts=[
            _make_spare_part("HP-001", source_chunk_id="chunk_001"),
            _make_spare_part("HP-002", source_chunk_id="chunk_002"),
        ]
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    ids = [i.identifier_id for i in identifiers]
    assert len(ids) == len(set(ids))


def test_normalized_value_strips_and_uppercases():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part(" hp 001 ")])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].normalized_value == "HP001"
    assert identifiers[0].raw_value == "hp 001"


def test_raw_value_is_stripped_of_outer_whitespace():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part("  HP-001  ")])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].raw_value == "HP-001"


def test_document_id_is_taken_from_graph():
    graph = _make_graph(document_id="doc_XYZ")
    extraction = _make_extraction(
        spare_parts=[_make_spare_part("HP-001", document_id="doc_XYZ")],
        document_id="doc_XYZ",
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers[0].document_id == "doc_XYZ"
