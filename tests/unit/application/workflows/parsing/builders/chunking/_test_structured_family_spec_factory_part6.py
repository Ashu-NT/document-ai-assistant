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

def test_fragment_builder_applies_report_specs_to_manual_classified_report_document() -> None:
    # Regression guard: a doc classified as MANUAL but whose title is "Final Inspection Report"
    # must still produce report structured chunks (the gate escape via REPORT_DOCUMENT_MARKERS).
    builder = make_builder()
    section = make_section(
        section_id="sec_hybrid_001",
        title="Final Inspection Report",
        section_path=["Final Inspection Report"],
        page=1,
    )
    elements = [
        make_element(
            element_id="txt_hybrid_001",
            text="Device information",
            page=1,
            reading_order=1,
        ),
        make_element(
            element_id="txt_hybrid_002",
            text="Serial number: PT-2024-00312; Tag number: FT-101",
            page=1,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Final Inspection Report Cerabar M",
        document_type=DocumentType.MANUAL,
        section=section,
        elements=elements,
    )

    device_info = next(
        (
            fragment
            for fragment in fragments
            if fragment.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
            and "PT-2024-00312" in fragment.text
        ),
        None,
    )

    assert device_info is not None, (
        "Report structured specs must activate for MANUAL-classified documents "
        "whose title contains 'final inspection report'"
    )
    assert device_info.section_path == section.section_path
    assert device_info.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    assert "PT-2024-00312" in device_info.text

def test_fragment_builder_applies_report_specs_via_document_sections_signal() -> None:
    # Regression guard: document_title="Pressure transmitter" contains no report marker, but
    # the document has sibling sections "Test Report" / "Final Inspection Report".
    # The gate must pass via document_sections_combined_text, not the title.
    builder = make_builder()
    section = make_section(
        section_id="sec_rpt_flat_001",
        title="Device information",
        section_path=["Device information"],
        page=2,
    )
    elements = [
        make_element(
            element_id="txt_rpt_flat_001",
            text="Device information",
            page=2,
            reading_order=1,
        ),
        make_element(
            element_id="txt_rpt_flat_002",
            text="Serial number: PT-2024-00312; Tag number: FT-101",
            page=2,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Pressure transmitter",
        document_type=DocumentType.MANUAL,
        section=section,
        elements=elements,
        document_sections_combined_text=(
            "Test Report > Final Inspection Report > Order information "
            "> Device information > Procedure > Measuring condition"
        ),
    )

    device_info = next(
        (
            f
            for f in fragments
            if f.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
            and "PT-2024-00312" in f.text
        ),
        None,
    )

    assert device_info is not None, (
        "Report specs must activate via document_sections_combined_text even when "
        "document_title ('Pressure transmitter') contains no report marker"
    )
    assert device_info.section_path == section.section_path
    assert device_info.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    assert "PT-2024-00312" in device_info.text

def test_fragment_builder_applies_datasheet_specs_via_document_sections_signal() -> None:
    # Regression guard: document_title contains no datasheet marker, but sibling sections
    # include "Ordering example" / "Technical Data".  Gate must pass via
    # document_sections_combined_text, not the title.
    builder = make_builder()
    section = make_section(
        section_id="sec_ds_flat_001",
        title="MK311xxx Ball Valve",
        section_path=["MK311xxx Ball Valve"],
        page=3,
    )
    elements = [
        make_element(
            element_id="txt_ds_flat_001",
            text="Ordering example",
            page=3,
            reading_order=1,
        ),
        make_element(
            element_id="txt_ds_flat_002",
            text="MK311007 = 2-way Wafer-type Ball valve, stainless steel, handle, DN 50.",
            page=3,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="DN25 DN80 MK311xxx",
        document_type=DocumentType.MANUAL,
        section=section,
        elements=elements,
        document_sections_combined_text=(
            "MK311xxx Ball Valve > Ordering example > Technical Data > Operating limits"
        ),
    )

    ordering_example = next(
        (
            f
            for f in fragments
            if f.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
            and "MK311007" in f.text
        ),
        None,
    )

    assert ordering_example is not None, (
        "Datasheet specs must activate via document_sections_combined_text even when "
        "document_title ('DN25 DN80 MK311xxx') contains no datasheet marker"
    )
    assert ordering_example.section_path == section.section_path
    assert ordering_example.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    assert "MK311007" in ordering_example.text

def test_fragment_builder_applies_certificate_specs_to_certificate_document_type() -> None:
    # Regression guard: a document classified as CERTIFICATE must activate the certificate
    # structured family builder and produce CERTIFICATION_INFO chunks even when the section
    # title alone does not contain certificate markers.
    builder = make_builder()
    section = make_section(
        section_id="sec_cert_001",
        title="General Information",
        section_path=["General Information"],
        page=1,
    )
    elements = [
        make_element(
            element_id="txt_cert_001",
            text="Certificate number: CERT-2024-00312",
            page=1,
            reading_order=1,
        ),
        make_element(
            element_id="txt_cert_002",
            text="Customer: ABC Shipping Ltd; Date of issue: 2024-03-15",
            page=1,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Test Certificate",
        document_type=DocumentType.CERTIFICATE,
        section=section,
        elements=elements,
    )

    general_info = next(
        (f for f in fragments if f.section_path == ["General Information"]),
        None,
    )

    assert general_info is not None, (
        "Certificate structured specs must activate for CERTIFICATE-classified documents "
        "whose content contains certificate general-information markers"
    )
    assert general_info.chunk_type == ChunkType.CERTIFICATION_INFO
    assert "CERT-2024-00312" in general_info.text
