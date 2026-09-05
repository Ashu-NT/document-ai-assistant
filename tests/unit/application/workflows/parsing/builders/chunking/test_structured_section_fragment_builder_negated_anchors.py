from src.application.workflows.parsing.builders.chunking.builders.structured import (
    StructuredFamilySpecFactory,
)
from src.application.workflows.parsing.builders.chunking.builders.structured_section_fragment_builder import (
    StructuredSectionFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import (
    ChunkType,
    DocumentType,
    ElementType,
    ParserMetadata,
    SourceLocation,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerStrength,
)
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


def make_section() -> DocumentSection:
    return DocumentSection(
        section_id="sec_pv_001",
        document_id="doc_001",
        title="Safe handling of pressure vessels",
        level=3,
        parent_section_id="sec_safety",
        section_path=[
            "2 For your safety",
            "2.4 Product safety",
            "Safe handling of pressure vessels",
        ],
        source=SourceLocation(page_start=12, page_end=12),
        sequence_number=1,
    )


def make_element(*, element_id: str, text: str, reading_order: int) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TEXT,
        text=text,
        reading_order=reading_order,
        source=SourceLocation(page_start=12, page_end=12),
        parser_metadata=ParserMetadata(
            parser_name="docling", parser_version="1.0", extra={}
        ),
    )


def make_builder() -> StructuredSectionFragmentBuilder:
    return StructuredSectionFragmentBuilder(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=400, chunk_overlap=20),
        spec_factory=StructuredFamilySpecFactory(enable_benchmark_tuning=False),
    )

def test_matches_markers_rejects_a_negated_availability_mention() -> None:
    builder = make_builder()

    text = (
        "pressurised vessel components cannot be obtained as spare parts "
        "because the vessels are only ever tested and documented as a unit"
    )

    markers = (
        EvidenceMarker(
            "spare parts",
            MarkerStrength.STRONG,
        ),
    )

    assert builder._matches_markers(
        text,
        markers,
    ) is False


def test_matches_markers_still_accepts_a_genuine_mention() -> None:
    builder = make_builder()

    text = (
        "see the spare parts list at the end of this manual "
        "for ordering codes"
    )

    markers = (
        EvidenceMarker(
            "spare parts",
            MarkerStrength.STRONG,
        ),
    )

    assert builder._matches_markers(
        text,
        markers,
    ) is True


def test_fragment_builder_does_not_tag_a_negated_spare_parts_mention_as_spare_parts_table() -> (
    None
):
    # Real document shape: a "Safe handling of pressure vessels" passage
    # under a safety section that happens to mention "spare parts" only to
    # say the components are NOT available as spare parts -- the real
    # content is a periodic inspection/replacement schedule, not a parts
    # list, and must not be hard-locked to SPARE_PARTS_TABLE.
    builder = make_builder()
    section = make_section()
    elements = [
        make_element(
            element_id="txt_001",
            text=(
                "Damaged pressure vessels should always be replaced completely. "
                "Pressurised vessel components cannot be obtained as spare parts "
                "because the vessels are only ever tested and documented as a unit."
            ),
            reading_order=1,
        ),
        make_element(
            element_id="txt_002",
            text="Check pressure vessels regularly internally and externally for corrosion damage.",
            reading_order=2,
        ),
        make_element(
            element_id="txt_003",
            text="Replace aluminium pressure vessel at the latest after 15 years.",
            reading_order=3,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Compressor Manual",
        document_type=DocumentType.MANUAL,
        section=section,
        elements=elements,
    )

    assert all(
        fragment.chunk_type != ChunkType.SPARE_PARTS_TABLE for fragment in fragments
    )
