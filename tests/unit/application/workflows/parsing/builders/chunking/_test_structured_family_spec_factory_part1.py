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

from src.domain.document import DocumentSection

from src.domain.elements import CanonicalElement

def make_section(
    *,
    section_id: str,
    title: str,
    section_path: list[str],
    page: int,
) -> DocumentSection:
    return DocumentSection(
        section_id=section_id,
        document_id="doc_001",
        title=title,
        level=2,
        parent_section_id="sec_parent",
        section_path=section_path,
        source=SourceLocation(page_start=page, page_end=page),
        sequence_number=1,
    )

def make_element(
    *,
    element_id: str,
    text: str,
    page: int,
    reading_order: int,
    element_type: ElementType = ElementType.TEXT,
    parser_extra: dict | None = None,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        reading_order=reading_order,
        source=SourceLocation(page_start=page, page_end=page),
        parser_metadata=(
            ParserMetadata(
                parser_name="docling",
                parser_version="1.0",
                extra=parser_extra or {},
            )
            if parser_extra is not None
            else None
        ),
    )

def make_builder() -> StructuredSectionFragmentBuilder:
    return StructuredSectionFragmentBuilder(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=220, chunk_overlap=20),
        spec_factory=StructuredFamilySpecFactory(enable_benchmark_tuning=False),
    )

def test_fragment_builder_detects_drawing_title_block_without_benchmark_identifiers() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_001",
        title="Arrangement details",
        section_path=["Arrangement details"],
        page=1,
    )
    elements = [
        make_element(
            element_id="txt_001",
            text="Drawing Number",
            page=1,
            reading_order=1,
        ),
        make_element(
            element_id="txt_002",
            text="A-100",
            page=1,
            reading_order=2,
        ),
        make_element(
            element_id="txt_003",
            text="Drawn by",
            page=1,
            reading_order=3,
        ),
        make_element(
            element_id="txt_004",
            text="Scale 1:50",
            page=1,
            reading_order=4,
        ),
    ]

    fragments, _ = builder.build(
        document_title="General arrangement drawing",
        document_type=DocumentType.DRAWING,
        section=section,
        elements=elements,
    )

    title_block = next(
        fragment
        for fragment in fragments
        if fragment.section_path == ["Title block"]
    )

    assert "A-100" in title_block.text

def test_fragment_builder_detects_certificate_particulars_from_generic_markers() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_002",
        title="Certificate",
        section_path=["Certificate"],
        page=1,
    )
    elements = [
        make_element(
            element_id="txt_010",
            text="Particulars",
            page=1,
            reading_order=1,
        ),
        make_element(
            element_id="txt_011",
            text="Quantity 2, Description safety valve, Nominal size DN50",
            page=1,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Inspection certificate",
        document_type=DocumentType.CERTIFICATE,
        section=section,
        elements=elements,
    )

    particulars = next(
        fragment
        for fragment in fragments
        if fragment.section_path == ["Certificate", "Particulars"]
    )

    assert particulars.chunk_type == ChunkType.CERTIFICATION_INFO
    assert "Nominal size DN50" in particulars.text

def test_fragment_builder_detects_certificate_cover_sheet_without_benchmark_values() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_002a",
        title="COVER SHEET",
        section_path=["COVER SHEET"],
        page=1,
    )
    elements = [
        make_element(
            element_id="txt_011a",
            text="Customer: Example Shipyard; Project: New Build 42; Model: Compact Fuel Unit; Series: 9606-382",
            page=1,
            reading_order=1,
        ),
        make_element(
            element_id="txt_011b",
            text="Revision 00; Edition 08.03.2022; Order No. 2452414325",
            page=1,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Fuel system certificate",
        document_type=DocumentType.CERTIFICATE,
        section=section,
        elements=elements,
    )

    cover_sheet = next(
        fragment
        for fragment in fragments
        if fragment.section_path == ["COVER SHEET"]
    )

    assert cover_sheet.chunk_type == ChunkType.CERTIFICATION_INFO
    assert "2452414325" in cover_sheet.text

def test_fragment_builder_detects_certificate_attachment_information_from_generic_markers() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_002b",
        title="Attachment",
        section_path=["Attachment"],
        page=2,
    )
    elements = [
        make_element(
            element_id="txt_011c",
            text="Areas inspected",
            page=2,
            reading_order=1,
        ),
        make_element(
            element_id="txt_011d",
            text="Food: Source and Storage. Water: Source and Distribution. Waste: Holding and Disposal. Medical facilities: Equipment and Medicines.",
            page=2,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Ship sanitation control exemption certificate",
        document_type=DocumentType.CERTIFICATE,
        section=section,
        elements=elements,
    )

    attachment = next(
        fragment
        for fragment in fragments
        if fragment.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    )

    assert "Medical facilities" in attachment.text

def test_fragment_builder_detects_datasheet_ordering_example_without_benchmark_code() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_003",
        title="Ordering",
        section_path=["Ordering"],
        page=2,
    )
    elements = [
        make_element(
            element_id="txt_020",
            text="Ordering example",
            page=2,
            reading_order=1,
        ),
        make_element(
            element_id="txt_021",
            text="Order code configuration example for selecting process connection and output signal.",
            page=2,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Pressure transmitter datasheet",
        document_type=DocumentType.DATASHEET,
        section=section,
        elements=elements,
    )

    ordering = next(
        fragment
        for fragment in fragments
        if fragment.section_path == ["Ordering example"]
    )

    assert ordering.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    assert "Order code" in ordering.text
