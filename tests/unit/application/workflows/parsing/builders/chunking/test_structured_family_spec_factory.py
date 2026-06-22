from src.application.workflows.parsing.builders.chunking.builders.structured import (
    StructuredFamilySpecFactory,
)
from src.application.workflows.parsing.builders.chunking.builders.structured_section_fragment_builder import (
    StructuredSectionFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import ChunkType, DocumentType, ElementType, SourceLocation
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
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        reading_order=reading_order,
        source=SourceLocation(page_start=page, page_end=page),
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


def test_fragment_builder_detects_maintenance_intervals_without_specific_hour_values() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_004",
        title="Maintenance",
        section_path=["Maintenance"],
        page=3,
    )
    elements = [
        make_element(
            element_id="txt_030",
            text="Maintenance interval",
            page=3,
            reading_order=1,
        ),
        make_element(
            element_id="txt_031",
            text="Inspect monthly and yearly during regular operating hours.",
            page=3,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Operating manual",
        document_type=DocumentType.MANUAL,
        section=section,
        elements=elements,
    )

    maintenance_interval = next(
        fragment
        for fragment in fragments
        if fragment.section_path == ["Maintenance", "Maintenance Intervals"]
    )

    assert maintenance_interval.chunk_type == ChunkType.MAINTENANCE_INTERVAL
    assert "monthly" in maintenance_interval.text.lower()


def test_fragment_builder_detects_troubleshooting_without_equipment_names() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_005",
        title="Maintenance",
        section_path=["Maintenance"],
        page=4,
    )
    elements = [
        make_element(
            element_id="txt_040",
            text="Troubleshooting",
            page=4,
            reading_order=1,
        ),
        make_element(
            element_id="txt_041",
            text="Possible cause: blocked inlet. Corrective action: inspect the filter and restart the unit.",
            page=4,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Service manual",
        document_type=DocumentType.MANUAL,
        section=section,
        elements=elements,
    )

    troubleshooting = next(
        fragment
        for fragment in fragments
        if fragment.section_path == ["Maintenance", "Troubleshooting"]
    )

    assert troubleshooting.chunk_type == ChunkType.TROUBLESHOOTING
    assert "Corrective action" in troubleshooting.text


def test_fragment_builder_keeps_certificate_identification_table_out_of_general_information() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_006",
        title="Remarks",
        section_path=["Remarks"],
        page=2,
    )
    elements = [
        make_element(
            element_id="txt_050",
            text="Office Hamburg",
            page=2,
            reading_order=1,
        ),
        make_element(
            element_id="tbl_051",
            text=(
                "| Description | Manufacturer Designation | Serial Number | IMO Number |\n"
                "|---|---|---|---|\n"
                "| 2 pcs., EC881-5 | L=500 mm, PN 350 bar | SL060323 | 0 |"
            ),
            page=2,
            reading_order=2,
            element_type=ElementType.TABLE,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Inspection certificate",
        document_type=DocumentType.CERTIFICATE,
        section=section,
        elements=elements,
    )

    assert any(
        fragment.section_path
        == ["Description / Manufacturer Designation / Serial Number table"]
        for fragment in fragments
    )
    assert all(
        fragment.section_path != ["General information"]
        for fragment in fragments
    )
    assert all(
        "Approval information" not in fragment.section_path
        for fragment in fragments
    )


def test_fragment_builder_keeps_certificate_results_under_results_section() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_007",
        title="Messdaten:/results",
        section_path=["Messdaten:/results"],
        page=3,
    )
    elements = [
        make_element(
            element_id="tbl_060",
            text=(
                "| Spezifikation/specification | Soll/nominal | Ist/result |\n"
                "|---|---|---|\n"
                "| Test pressure nominal | 700 bar | 730 bar |"
            ),
            page=3,
            reading_order=1,
            element_type=ElementType.TABLE,
        ),
        make_element(
            element_id="txt_061",
            text="Part number SL060323; hose length 500 mm; operation pressure 350 bar.",
            page=3,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Inspection certificate",
        document_type=DocumentType.CERTIFICATE,
        section=section,
        elements=elements,
    )

    assert any(
        fragment.section_path == ["Messdaten:/results"]
        and fragment.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
        for fragment in fragments
    )
    assert all(
        "Approval information" not in fragment.section_path
        for fragment in fragments
    )
    assert all(
        fragment.section_path != ["Particulars"]
        for fragment in fragments
    )
