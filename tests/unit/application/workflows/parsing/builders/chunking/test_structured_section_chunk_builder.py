from src.application.workflows.parsing.builders.chunking import SectionChunkBuilder
from src.domain.common import DocumentType, ElementType, SourceLocation, ChunkType
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
    element_type: ElementType,
    text: str,
    page: int,
    reading_order: int,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        reading_order=reading_order,
        source=SourceLocation(page_start=page, page_end=page),
    )


def test_section_chunk_builder_sanitizes_branding_noise_from_section_paths() -> None:
    builder = SectionChunkBuilder()
    section = make_section(
        section_id="sec_001",
        title="6.3 Operation Macerator",
        section_path=[
            "6 Operation & General Maintenance",
            "Environmentally",
            "Responsible Solutions",
            "Engineered",
            "6.3 Operation Macerator",
        ],
        page=24,
    )
    elements = [
        make_element(
            element_id="txt_001",
            element_type=ElementType.TEXT,
            text="Start/Run illuminated solid green; fill food, close lid, press Start/Run.",
            page=24,
            reading_order=1,
        )
    ]

    payloads = builder.build_chunk_payloads(
        document_title="FWC12 Technical Manual",
        section=section,
        elements=elements,
        document_type=DocumentType.MANUAL,
    )

    assert payloads[0].section_path == [
        "6 Operation & General Maintenance",
        "6.3 Operation Macerator",
    ]


def test_section_chunk_builder_resets_numbered_sibling_paths() -> None:
    builder = SectionChunkBuilder()
    section = make_section(
        section_id="sec_001a",
        title="Technical Data",
        section_path=[
            "7 Components",
            "7.2 Food Waste Press",
            "Safety Precautions 7.2.1",
            "Owner / User Responsibility",
            "General Warnings:",
            "Electrical System Precautions",
            "Biohazard",
            "Food Waste Press Description 7.2.2",
            "Technical Data",
        ],
        page=50,
    )
    elements = [
        make_element(
            element_id="txt_001a",
            element_type=ElementType.TEXT,
            text="Press Type TSP20 Serial Number 221010004Z507",
            page=50,
            reading_order=1,
        )
    ]

    payloads = builder.build_chunk_payloads(
        document_title="FWC12 Technical Manual",
        section=section,
        elements=elements,
        document_type=DocumentType.MANUAL,
    )

    assert payloads[0].section_path == [
        "7 Components",
        "7.2 Food Waste Press",
        "Food Waste Press Description 7.2.2",
        "Technical Data",
    ]


def test_section_chunk_builder_emits_manual_maintenance_interval_chunk() -> None:
    builder = SectionChunkBuilder()
    section = make_section(
        section_id="sec_002",
        title="Maintenance",
        section_path=["7 Components", "7.1 Macerators", "Maintenance"],
        page=32,
    )
    elements = [
        make_element(
            element_id="txt_010",
            element_type=ElementType.TEXT,
            text="Maintenance Intervals",
            page=32,
            reading_order=1,
        ),
        make_element(
            element_id="txt_011",
            element_type=ElementType.TEXT,
            text="Cleaning after daily use. Preventive Maintenance 1 first after 1 month then after 1 year and 3 yearly. Wear replacement after approx. 9000 operating hours.",
            page=32,
            reading_order=2,
        ),
    ]

    payloads = builder.build_chunk_payloads(
        document_title="FWC12 Technical Manual",
        section=section,
        elements=elements,
        document_type=DocumentType.MANUAL,
    )

    interval_payload = next(
        payload
        for payload in payloads
        if payload.section_path
        == [
            "7 Components",
            "7.1 Macerators",
            "Maintenance",
            "Maintenance Intervals",
        ]
    )

    assert interval_payload.chunk_type == ChunkType.MAINTENANCE_INTERVAL
    assert "9000 operating hours" in interval_payload.content


def test_section_chunk_builder_resets_path_when_manual_sections_advance() -> None:
    builder = SectionChunkBuilder()
    section = make_section(
        section_id="sec_002a",
        title="Trouble Shooting 7.1.10",
        section_path=[
            "7 Components",
            "7.1 Macerators",
            "Commissioning & Shutdown 7.1.8",
            "Check before Start Up",
            "Checks during Start Up",
            "Operation 7.1.9",
            "Start and stop",
            "Trouble Shooting 7.1.10",
        ],
        page=33,
    )
    elements = [
        make_element(
            element_id="txt_010a",
            element_type=ElementType.TEXT,
            text="Possible cause blocked inlet. Corrective action inspect and clear the inlet.",
            page=33,
            reading_order=1,
        )
    ]

    payloads = builder.build_chunk_payloads(
        document_title="FWC12 Technical Manual",
        section=section,
        elements=elements,
        document_type=DocumentType.MANUAL,
    )

    assert payloads[0].section_path == [
        "7 Components",
        "7.1 Macerators",
        "Trouble Shooting 7.1.10",
    ]


def test_section_chunk_builder_emits_report_connection_procedure_chunk() -> None:
    builder = SectionChunkBuilder()
    section = make_section(
        section_id="sec_003",
        title="Electrical connection",
        section_path=["6 Electrical connection"],
        page=12,
    )
    elements = [
        make_element(
            element_id="txt_020",
            element_type=ElementType.TEXT,
            text="Connect the device in the following order:",
            page=12,
            reading_order=1,
        ),
        make_element(
            element_id="txt_021",
            element_type=ElementType.TEXT,
            text="Check supply voltage, switch off supply voltage, remove housing cover, guide cable through gland, connect according to diagram.",
            page=12,
            reading_order=2,
        ),
    ]

    payloads = builder.build_chunk_payloads(
        document_title="Pressure transmitter report",
        section=section,
        elements=elements,
        document_type=DocumentType.REPORT,
    )

    procedure_payload = next(
        payload
        for payload in payloads
        if payload.section_path
        == [
            "Brief Operating Instructions",
            "6 Electrical connection",
            "6.2 Connecting the device",
        ]
    )

    assert procedure_payload.chunk_type == ChunkType.OPERATION_INSTRUCTION
    assert "switch off supply voltage" in procedure_payload.content.lower()
