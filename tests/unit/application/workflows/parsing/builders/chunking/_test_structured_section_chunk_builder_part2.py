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
        if payload.chunk_type == ChunkType.OPERATION_INSTRUCTION
    )

    assert procedure_payload.section_path == section.section_path
    assert procedure_payload.chunk_type == ChunkType.OPERATION_INSTRUCTION
    assert "switch off supply voltage" in procedure_payload.content.lower()
