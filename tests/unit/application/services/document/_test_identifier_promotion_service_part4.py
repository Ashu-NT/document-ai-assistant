from __future__ import annotations

import pytest

from src.application.services.document.identifiers.identifier_promotion_service import (
    IdentifierPromotionService,
)

from src.domain.common.enums import IdentifierType

from src.domain.document import Document, DocumentChunk, DocumentGraph

from src.domain.document.value_objects import DocumentHashes

from src.domain.common import ChunkType, DocumentType, SourceLocation

from src.domain.extraction.contact_point import ContactPoint, ContactPointType

from src.domain.extraction.equipment_info import EquipmentInfo

from src.domain.extraction.extracted_identifier import ExtractedIdentifier

from src.domain.extraction.extraction_result import ExtractionResult

from src.domain.extraction.manufacturer import Manufacturer

from src.domain.extraction.semantic_relationship import SemanticEntityType

from src.domain.extraction.spare_part import SparePart

from src.shared.ids import IdGenerator

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
    contact_points: list[ContactPoint] | None = None,
    document_id: str = "doc_001",
) -> ExtractionResult:
    return ExtractionResult(
        extraction_id="extraction_001",
        document_id=document_id,
        spare_parts=spare_parts or [],
        equipment=equipment or [],
        contact_points=contact_points or [],
    )

def _make_contact_point(
    *,
    value: str = "service@example.com",
    contact_type: ContactPointType = ContactPointType.EMAIL_ADDRESS,
    owner_name: str | None = "Example Manufacturer",
    owner_entity_type: SemanticEntityType | None = SemanticEntityType.MANUFACTURER,
    document_id: str = "doc_001",
    source_chunk_id: str | None = "chunk_001",
    confidence_score: float | None = 0.9,
) -> ContactPoint:
    return ContactPoint(
        contact_point_id="contact_point_001",
        document_id=document_id,
        contact_type=contact_type,
        value=value,
        owner_name=owner_name,
        owner_entity_type=owner_entity_type,
        source_chunk_id=source_chunk_id,
        confidence_score=confidence_score,
    )

def _service() -> IdentifierPromotionService:
    return IdentifierPromotionService()

def _make_manufacturer(
    name: str = "Grundfos",
    document_id: str = "doc_001",
    source_chunk_id: str | None = "chunk_001",
    confidence_score: float | None = 0.9,
) -> Manufacturer:
    return Manufacturer(
        manufacturer_id="mfr_001",
        document_id=document_id,
        name=name,
        source_chunk_id=source_chunk_id,
        confidence_score=confidence_score,
    )

def _make_extraction_with_manufacturers(
    manufacturers: list[Manufacturer] | None = None,
    document_id: str = "doc_001",
) -> ExtractionResult:
    return ExtractionResult(
        extraction_id="extraction_001",
        document_id=document_id,
        manufacturers=manufacturers or [],
    )

def test_promote_extracted_identifier_ignores_non_identifier_metadata_without_warning(
    raw_identifier_type: str,
    raw_value: str,
    caplog,
):
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value=raw_value,
                identifier_type=raw_identifier_type,
                source_chunk_id="chunk_001",
                confidence_score=0.9,
            )
        ],
    )

    with caplog.at_level("WARNING"):
        identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []
    assert caplog.records == []

def test_promote_extracted_identifier_ignores_internal_chunk_id_without_warning(caplog):
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value="chunk_2f914a1d29194505ad08dce828fa0a3c",
                identifier_type="chunk_id",
                source_chunk_id="chunk_001",
                confidence_score=0.9,
            )
        ],
    )

    with caplog.at_level("WARNING"):
        identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []
    assert caplog.records == []

def test_promote_extracted_identifier_ignores_echoed_source_chunk_id_without_warning(
    caplog,
):
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value="chunk_001",
                identifier_type="unknown",
                source_chunk_id="chunk_001",
                confidence_score=0.9,
            )
        ],
    )

    with caplog.at_level("WARNING"):
        identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []
    assert caplog.records == []

def test_promote_extracted_identifier_deduped_against_structured():
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        spare_parts=[_make_spare_part("HP-001")],
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value="HP-001",
                identifier_type="part_number",
                source_chunk_id="chunk_001",
                confidence_score=0.9,
            )
        ],
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].raw_value == "HP-001"

def test_promote_multiple_extracted_identifiers():
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value="DRG-5001",
                identifier_type="drawing_number",
                source_chunk_id="chunk_001",
                confidence_score=0.9,
            ),
            ExtractedIdentifier(
                raw_value="ISO 9001",
                identifier_type="certificate_number",
                source_chunk_id="chunk_001",
                confidence_score=0.95,
            ),
        ],
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 2
    types = {i.identifier_type for i in identifiers}
    assert IdentifierType.DRAWING_NUMBER in types
    assert IdentifierType.CERTIFICATE_NUMBER in types

def test_default_min_length_allows_short_values():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part("A1")])
    identifiers = IdentifierPromotionService().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].raw_value == "A1"

def test_min_length_filters_out_short_normalized_values():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part("A1")])
    service = IdentifierPromotionService(min_length=3)
    identifiers = service.promote(extraction, graph, IdGenerator())

    assert identifiers == []

def test_min_length_keeps_values_meeting_the_threshold():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part("HP-001")])
    service = IdentifierPromotionService(min_length=3)
    identifiers = service.promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].raw_value == "HP-001"
