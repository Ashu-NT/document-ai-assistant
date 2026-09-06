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

def test_fragment_builder_uses_full_section_when_path_identifies_troubleshooting() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_005b",
        title="Trouble-Shooting 7.3.10",
        section_path=[
            "7 Components",
            "7.3 Vacuum / Transfer Pump",
            "Trouble-Shooting 7.3.10",
        ],
        page=5,
    )
    elements = [
        make_element(
            element_id="txt_041c",
            text="The pump will not start.",
            page=5,
            reading_order=1,
        ),
        make_element(
            element_id="txt_041d",
            text="Possible causes and remedies are listed in the table below.",
            page=5,
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

    assert "The pump will not start." in troubleshooting.text
    assert "Possible causes and remedies" in troubleshooting.text

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
        fragment.section_path == section.section_path
        and "Serial Number" in fragment.text
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

def test_fragment_builder_emits_report_procedure_chunk() -> None:
    builder = make_builder()
    section = make_section(
        section_id="sec_rpt_001",
        title="Final Inspection Report",
        section_path=["Final Inspection Report"],
        page=1,
    )
    elements = [
        make_element(
            element_id="txt_rpt_001",
            text="Test specification P0043",
            page=1,
            reading_order=1,
        ),
        make_element(
            element_id="txt_rpt_002",
            text="Test rig L230; reference standard ETS-100",
            page=1,
            reading_order=2,
        ),
    ]

    fragments, _ = builder.build(
        document_title="Final Inspection Report",
        document_type=DocumentType.REPORT,
        section=section,
        elements=elements,
    )

    procedure = next(
        (
            fragment
            for fragment in fragments
            if fragment.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
            and "P0043" in fragment.text
        ),
        None,
    )

    assert procedure is not None
    assert procedure.section_path == section.section_path
    assert procedure.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    assert "P0043" in procedure.text
