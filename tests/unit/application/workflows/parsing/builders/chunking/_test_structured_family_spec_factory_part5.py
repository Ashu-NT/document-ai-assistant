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

def test_fragment_builder_emits_report_mounting_chunk() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_rpt_002",
        title="Brief Operating Instructions",
        section_path=["Brief Operating Instructions"],
        page=9,
    )
    elements = [
        make_element(
            element_id="txt_rpt_010",
            text="Mounting instructions for process connection",
            page=9,
            reading_order=1,
        ),
        make_element(
            element_id="txt_rpt_011",
            text="NPT tightening torque: 25 Nm (18.4 lbf ft)",
            page=9,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Final Inspection Report",
        document_type=DocumentType.REPORT,
        section=section,
        elements=elements,
    )

    mounting = next(
        (
            fragment
            for fragment in fragments
            if fragment.chunk_type == ChunkType.INSTALLATION_INSTRUCTION
            and "25 Nm" in fragment.text
        ),
        None,
    )

    assert mounting is not None
    assert mounting.section_path == section.section_path
    assert mounting.chunk_type == ChunkType.INSTALLATION_INSTRUCTION
    assert "25 Nm" in mounting.text

def test_fragment_builder_emits_report_operation_options_chunk() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_rpt_003",
        title="Brief Operating Instructions",
        section_path=["Brief Operating Instructions"],
        page=18,
    )
    elements = [
        make_element(
            element_id="txt_rpt_020",
            text="Operation options for zero and span calibration",
            page=18,
            reading_order=1,
        ),
        make_element(
            element_id="txt_rpt_021",
            text="Press and hold push button for 12 seconds to reset to factory defaults.",
            page=18,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Final Inspection Report",
        document_type=DocumentType.REPORT,
        section=section,
        elements=elements,
    )

    op_options = next(
        (
            fragment
            for fragment in fragments
            if fragment.chunk_type == ChunkType.OPERATION_INSTRUCTION
            and "12 seconds" in fragment.text
        ),
        None,
    )

    assert op_options is not None
    assert op_options.section_path == section.section_path
    assert op_options.chunk_type == ChunkType.OPERATION_INSTRUCTION
    assert "12 seconds" in op_options.text

def test_fragment_builder_emits_report_performance_data_chunk() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_rpt_004",
        title="Performance Data 100%",
        section_path=["Performance Data 100%"],
        page=9,
    )
    elements = [
        make_element(
            element_id="txt_rpt_030",
            text="Performance Data",
            page=9,
            reading_order=1,
        ),
        make_element(
            element_id="txt_rpt_031",
            text="Engine power 2400 kW; engine speed 2000 rpm; fuel consumption 208 g/kWh.",
            page=9,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Shop test protocol",
        document_type=DocumentType.REPORT,
        section=section,
        elements=elements,
    )

    performance = next(
        (
            fragment
            for fragment in fragments
            if fragment.section_path == ["Performance Data 100%"]
        ),
        None,
    )

    assert performance is not None
    assert performance.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    assert "fuel consumption" in performance.text.lower()

def test_fragment_builder_applies_datasheet_specs_to_manual_classified_datasheet_document() -> None:
    # Regression guard: a doc classified as MANUAL but whose content contains "ordering example"
    # (a DATASHEET_DOCUMENT_MARKER) must still produce datasheet structured chunks.
    builder = make_builder()
    section = make_section(
        section_id="sec_ds_001",
        title="MK311xxx Ball Valve",
        section_path=["MK311xxx Ball Valve"],
        page=2,
    )
    elements = [
        make_element(
            element_id="txt_ds_001",
            text="Ordering example",
            page=2,
            reading_order=1,
        ),
        make_element(
            element_id="txt_ds_002",
            text="MK311007 = 2-way Wafer-type Ball valve, stainless steel, handle, DN 50.",
            page=2,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="DN25 - DN80 MK311xxx Datasheet",
        document_type=DocumentType.MANUAL,
        section=section,
        elements=elements,
    )

    ordering_example = next(
        (
            fragment
            for fragment in fragments
            if fragment.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
            and "MK311007" in fragment.text
        ),
        None,
    )

    assert ordering_example is not None, (
        "Datasheet structured specs must activate for MANUAL-classified documents "
        "whose content contains 'ordering example'"
    )
    assert ordering_example.section_path == section.section_path
    assert ordering_example.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    assert "MK311007" in ordering_example.text
