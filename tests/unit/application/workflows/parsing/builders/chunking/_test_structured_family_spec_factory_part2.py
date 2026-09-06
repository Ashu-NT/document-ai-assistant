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

def test_fragment_builder_detects_datasheet_cooling_system_without_exact_values() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_003a",
        title="Cooling system",
        section_path=["Cooling system"],
        page=3,
    )
    elements = [
        make_element(
            element_id="txt_021a",
            text="Cooling system",
            page=3,
            reading_order=1,
        ),
        make_element(
            element_id="txt_021b",
            text="Cooling water inlet and coolant return values are listed for each operating point.",
            page=3,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Permanent magnet motor datasheet",
        document_type=DocumentType.DATASHEET,
        section=section,
        elements=elements,
    )

    cooling = next(
        fragment
        for fragment in fragments
        if fragment.section_path == ["Cooling system"]
    )

    assert cooling.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    assert "cooling water inlet" in cooling.text.lower()

def test_fragment_builder_detects_datasheet_sensor_information_without_part_numbers() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_003b",
        title="Sensors",
        section_path=["Sensors"],
        page=4,
    )
    elements = [
        make_element(
            element_id="txt_021c",
            text="Sensors",
            page=4,
            reading_order=1,
        ),
        make_element(
            element_id="txt_021d",
            text="Temperature sensors and encoder feedback are installed for monitoring and speed control.",
            page=4,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Motor datasheet",
        document_type=DocumentType.DATASHEET,
        section=section,
        elements=elements,
    )

    sensors = next(
        fragment
        for fragment in fragments
        if fragment.section_path == ["Sensors"]
    )

    assert sensors.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    assert "encoder feedback" in sensors.text.lower()

def test_fragment_builder_detects_datasheet_technical_features_from_generic_markers() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_003c",
        title="caratteristiche tecniche",
        section_path=["caratteristiche tecniche"],
        page=2,
    )
    elements = [
        make_element(
            element_id="txt_021e",
            text="caratteristiche tecniche",
            page=2,
            reading_order=1,
        ),
        make_element(
            element_id="txt_021f",
            text="Technical features include AISI 316 housing and marine-grade sealing materials.",
            page=2,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Deck filler datasheet",
        document_type=DocumentType.DATASHEET,
        section=section,
        elements=elements,
    )

    technical_features = next(
        fragment
        for fragment in fragments
        if fragment.section_path == ["caratteristiche tecniche"]
    )

    assert technical_features.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    assert "aisi 316" in technical_features.text.lower()

def test_fragment_builder_detects_datasheet_installation_maintenance_from_generic_markers() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_003d",
        title="Istruzioni di montaggio e manutenzione",
        section_path=["Istruzioni di montaggio e manutenzione"],
        page=5,
    )
    elements = [
        make_element(
            element_id="txt_021g",
            text="Istruzioni di montaggio e manutenzione",
            page=5,
            reading_order=1,
        ),
        make_element(
            element_id="txt_021h",
            text="Installation instructions and maintenance steps must be followed before commissioning the unit.",
            page=5,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Deck filler datasheet",
        document_type=DocumentType.DATASHEET,
        section=section,
        elements=elements,
    )

    installation_maintenance = next(
        fragment
        for fragment in fragments
        if fragment.section_path == ["Istruzioni di montaggio e manutenzione"]
    )

    assert installation_maintenance.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    assert "commissioning" in installation_maintenance.text.lower()

def test_fragment_builder_does_not_bleed_datasheet_connection_family_into_manual_maintenance() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_manual_maintenance",
        title="Maintenance 7.1.11",
        section_path=["7 Components", "7.1 Macerators", "Maintenance 7.1.11"],
        page=32,
    )
    elements = [
        make_element(
            element_id="txt_manual_001",
            text="Maintenance Intervals",
            page=32,
            reading_order=1,
        ),
        make_element(
            element_id="txt_manual_002",
            text=(
                "Preventive maintenance 1 first time after 1 month use, then after 1 year. "
                "Check electrical connections. Check pipe connections for leaks."
            ),
            page=32,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="FWC12 Technical Manual",
        document_type=DocumentType.MANUAL,
        section=section,
        elements=elements,
        document_sections_combined_text=(
            "Technical Data / Specification > Ordering example > Operating limits"
        ),
    )

    assert not any(
        fragment.section_path == ["CONNECTION"] for fragment in fragments
    )
    assert not any(
        fragment.section_path == ["Technical Data / Specification"]
        for fragment in fragments
    )
    assert any(
        fragment.section_path == section.section_path
        and fragment.chunk_type == ChunkType.MAINTENANCE_INTERVAL
        for fragment in fragments
    )
