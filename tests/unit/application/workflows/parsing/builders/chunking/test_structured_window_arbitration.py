from src.application.workflows.parsing.builders.chunking import SectionChunkBuilder
from src.application.workflows.parsing.builders.chunking.builders.structured.arbitration import (
    StructuredWindowArbitrator,
    StructuredWindowCandidate,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerStrength,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_evidence_family import (
    StructuredEvidenceFamily,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_section_window_spec import (
    StructuredSectionWindowSpec,
)
from src.domain.common import ChunkType, DocumentType, ElementType, SourceLocation
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


def _section(title: str = "Intended use") -> DocumentSection:
    return DocumentSection(
        section_id="sec_001",
        document_id="doc_001",
        title=title,
        level=2,
        section_path=["2 Safety", title],
        source=SourceLocation(page_start=13, page_end=13),
        sequence_number=1,
    )


def _element(element_id: str, text: str, order: int) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TEXT,
        text=text,
        reading_order=order,
        source=SourceLocation(page_start=13, page_end=13),
    )


def _spec(chunk_type: ChunkType) -> StructuredSectionWindowSpec:
    return StructuredSectionWindowSpec(
        family=StructuredEvidenceFamily.MANUAL_MAINTENANCE_INTERVAL,
        section_path=["Section"],
        anchor_markers=(
            EvidenceMarker("maintenance interval", MarkerStrength.STRONG),
        ),
        chunk_type=chunk_type,
    )


def _candidate(
    *,
    chunk_type: ChunkType,
    elements: tuple[CanonicalElement, ...],
    anchors: frozenset[str],
    score: int,
    direct: bool,
) -> StructuredWindowCandidate:
    return StructuredWindowCandidate(
        spec=_spec(chunk_type),
        elements=elements,
        anchor_element_ids=anchors,
        score=score,
        direct_evidence=direct,
    )


def test_reference_only_mentions_do_not_create_structured_chunk_types() -> None:
    elements = [
        _element(
            "e1",
            "Use permissible parameters in accordance with the Technical Data.",
            1,
        ),
        _element(
            "e2",
            "Use approved replacements; refer to the Spare Parts Catalog.",
            2,
        ),
        _element(
            "e3",
            "Intervals are specified in the Maintenance Schedule.",
            3,
        ),
        _element(
            "e4",
            "The equipment shall be operated only for its intended purpose.",
            4,
        ),
    ]

    payloads = SectionChunkBuilder().build_chunk_payloads(
        document_title="Marine engine operating manual",
        document_type=DocumentType.MANUAL,
        section=_section(),
        elements=elements,
    )

    assert payloads
    assert all(payload.chunk_type == ChunkType.GENERAL for payload in payloads)
    combined = "\n".join(payload.content for payload in payloads)
    assert "Spare Parts Catalog" in combined
    assert "Maintenance Schedule" in combined


def test_ambiguous_same_span_labels_fall_back_to_ordinary_evidence() -> None:
    element = _element("e1", "Ambiguous evidence", 1)
    candidates = [
        _candidate(
            chunk_type=ChunkType.MAINTENANCE_INTERVAL,
            elements=(element,),
            anchors=frozenset({"e1"}),
            score=8,
            direct=False,
        ),
        _candidate(
            chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
            elements=(element,),
            anchors=frozenset({"e1"}),
            score=8,
            direct=False,
        ),
    ]

    assert StructuredWindowArbitrator().select(candidates) == []


def test_direct_evidence_wins_competing_overlap() -> None:
    element = _element("e1", "Interval | Task\n500 hours | Inspect", 1)
    direct = _candidate(
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        elements=(element,),
        anchors=frozenset({"e1"}),
        score=14,
        direct=True,
    )
    incidental = _candidate(
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        elements=(element,),
        anchors=frozenset({"e1"}),
        score=8,
        direct=False,
    )

    assert StructuredWindowArbitrator().select([incidental, direct]) == [direct]


def test_distinct_direct_evidence_types_in_one_section_are_preserved() -> None:
    interval = _element("e1", "Every 500 hours inspect the filter.", 1)
    specification = _element("e2", "Rated voltage: 400 V.", 2)
    all_elements = (interval, specification)
    interval_candidate = _candidate(
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        elements=all_elements,
        anchors=frozenset({"e1"}),
        score=14,
        direct=True,
    )
    specification_candidate = _candidate(
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        elements=all_elements,
        anchors=frozenset({"e2"}),
        score=14,
        direct=True,
    )

    selected = StructuredWindowArbitrator().select(
        [interval_candidate, specification_candidate]
    )

    assert selected == [interval_candidate, specification_candidate]
