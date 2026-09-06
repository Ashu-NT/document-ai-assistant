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

def test_fragment_builder_keeps_manual_maintenance_family_when_sensor_list_exists_elsewhere() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_manual_maintenance_sensor",
        title="Maintenance 7.1.11",
        section_path=["7 Components", "7.1 Macerators", "Maintenance 7.1.11"],
        page=32,
    )
    elements = [
        make_element(
            element_id="txt_manual_sensor_001",
            text="Maintenance Intervals",
            page=32,
            reading_order=1,
        ),
        make_element(
            element_id="tbl_manual_sensor_001",
            text=(
                "| Description | Interval | Drive Type |\n"
                "| Clean rotor | monthly | BF30 |\n"
                "| Inspect seal | yearly | BF30 |"
            ),
            page=32,
            reading_order=2,
            element_type=ElementType.TABLE,
        ),
    ]

    fragments, _ = builder.build(
        document_title="FWC12 Technical Manual",
        document_type=DocumentType.MANUAL,
        section=section,
        elements=elements,
        document_sections_combined_text=(
            "7 Components > 7.1 Macerators > Maintenance 7.1.11 > "
            "7 Components > 7.6 Sensor List"
        ),
    )

    assert any(
        fragment.section_path == section.section_path
        and fragment.chunk_type == ChunkType.MAINTENANCE_INTERVAL
        for fragment in fragments
    )
    assert not any(
        fragment.section_path == ["Sensor List"]
        for fragment in fragments
    )

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
        if fragment.chunk_type == ChunkType.MAINTENANCE_INTERVAL
    )

    assert maintenance_interval.section_path == section.section_path
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
        if fragment.chunk_type == ChunkType.TROUBLESHOOTING
    )

    assert troubleshooting.section_path == section.section_path
    assert troubleshooting.chunk_type == ChunkType.TROUBLESHOOTING
    assert "Corrective action" in troubleshooting.text

def test_fragment_builder_detects_hyphenated_troubleshooting_heading() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_005a",
        title="Trouble-Shooting 7.3.10",
        section_path=[
            "7 Components",
            "7.3 Vacuum / Transfer Pump",
            "Trouble-Shooting 7.3.10",
        ],
        page=4,
    )
    elements = [
        make_element(
            element_id="txt_041a",
            text="The troubleshooting charts list possible problems, probable causes and potential remedies.",
            page=4,
            reading_order=1,
        ),
        make_element(
            element_id="txt_041b",
            text="Possible cause: blocked inlet. Potential remedy: inspect the filter and restart the unit.",
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
        if fragment.chunk_type == ChunkType.TROUBLESHOOTING
    )

    assert "Potential remedy" in troubleshooting.text
    assert troubleshooting.section_path == [
        "7 Components",
        "7.3 Vacuum / Transfer Pump",
        "Trouble-Shooting 7.3.10",
    ]
