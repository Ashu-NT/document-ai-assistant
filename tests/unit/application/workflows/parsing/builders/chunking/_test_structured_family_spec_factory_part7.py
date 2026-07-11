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

def test_fragment_builder_applies_certificate_specs_via_document_sections_signal() -> None:
    # Regression guard: document_title contains no certificate marker, but sibling sections
    # include "inspection certificate".  Gate must pass via document_sections_combined_text.
    builder = make_builder()
    section = make_section(
        section_id="sec_cert_flat_001",
        title="General Information",
        section_path=["General Information"],
        page=1,
    )
    elements = [
        make_element(
            element_id="txt_cert_flat_001",
            text="Certificate number: CERT-2024-00312",
            page=1,
            reading_order=1,
        ),
        make_element(
            element_id="txt_cert_flat_002",
            text="Customer: ABC Shipping Ltd",
            page=1,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Pressure Transmitter PT-500",
        document_type=DocumentType.MANUAL,
        section=section,
        elements=elements,
        document_sections_combined_text=(
            "Inspection Certificate > General Information > Particulars > Test Data"
        ),
    )

    general_info = next(
        (f for f in fragments if f.section_path == ["General Information"]),
        None,
    )

    assert general_info is not None, (
        "Certificate specs must activate via document_sections_combined_text even when "
        "document_title ('Pressure Transmitter PT-500') contains no certificate marker"
    )
    assert general_info.chunk_type == ChunkType.CERTIFICATION_INFO
    assert "CERT-2024-00312" in general_info.text

def test_fragment_builder_combines_particulars_rows_when_section_path_identifies_section() -> None:
    """When the section path explicitly names 'Particulars', all element rows must be
    captured in a single CERTIFICATION_INFO fragment even when individual element texts
    do not contain standard anchor-marker words (e.g., pure-value rows like '4 pcs')."""
    builder = make_builder()
    section = make_section(
        section_id="sec_part_001",
        title="Particulars",
        section_path=["Certificate", "Particulars"],
        page=2,
    )
    # Simulate a certificate where each Particulars row is a separate element
    # and the text contains only the value (not the field label).
    elements = [
        make_element(element_id="e_qty", text="4 pcs", page=2, reading_order=1),
        make_element(
            element_id="e_size",
            text="DN 8 (for 1/4\" hose connection)",
            page=2,
            reading_order=2,
        ),
        make_element(element_id="e_type", text="Ball valve", page=2, reading_order=3),
    ]

    fragments, _ = builder.build(
        document_title="Inspection certificate",
        document_type=DocumentType.CERTIFICATE,
        section=section,
        elements=elements,
    )

    cert_frags = [f for f in fragments if f.chunk_type == ChunkType.CERTIFICATION_INFO]
    assert cert_frags, "At least one CERTIFICATION_INFO fragment must be produced"

    combined = next(
        (f for f in cert_frags if "4 pcs" in f.text and "DN 8" in f.text),
        None,
    )
    assert combined is not None, (
        "Both '4 pcs' and 'DN 8' must appear together in a single CERTIFICATION_INFO "
        "fragment when section path identifies a Particulars section"
    )
    assert "Ball valve" in combined.text

def test_fragment_builder_particulars_combine_all_windows_merges_multiple_anchors() -> None:
    """When multiple elements in the Particulars section each contain anchor words,
    combine_all_windows must merge them into one fragment rather than N separate ones."""
    builder = make_builder()
    section = make_section(
        section_id="sec_part_002",
        title="Particulars",
        section_path=["Certificate", "Particulars"],
        page=3,
    )
    # Elements where BOTH contain anchor words — without combine_all_windows these
    # would produce two overlapping windows → two fragments.
    elements = [
        make_element(
            element_id="e_qty_label",
            text="Quantity: 4 pcs",
            page=3,
            reading_order=1,
        ),
        make_element(
            element_id="e_size_label",
            text="Size: DN 8",
            page=3,
            reading_order=2,
        ),
        make_element(
            element_id="e_type_label",
            text="Type: DHSF-0.25",
            page=3,
            reading_order=3,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Inspection certificate",
        document_type=DocumentType.CERTIFICATE,
        section=section,
        elements=elements,
    )

    cert_frags = [f for f in fragments if f.chunk_type == ChunkType.CERTIFICATION_INFO]
    # All content must be in a single combined fragment, not three separate ones.
    combined = next(
        (
            f
            for f in cert_frags
            if "4 pcs" in f.text and "DN 8" in f.text and "DHSF-0.25" in f.text
        ),
        None,
    )
    assert combined is not None, (
        "Particulars with multiple anchor rows must produce one combined fragment "
        "containing all rows, not separate per-anchor fragments"
    )
