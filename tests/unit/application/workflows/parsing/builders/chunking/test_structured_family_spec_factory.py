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
            if fragment.section_path == ["Final Inspection Report", "Procedure"]
        ),
        None,
    )

    assert procedure is not None
    assert procedure.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    assert "P0043" in procedure.text


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
            if fragment.section_path
            == ["Brief Operating Instructions", "5 Mounting"]
        ),
        None,
    )

    assert mounting is not None
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
            if fragment.section_path
            == ["Brief Operating Instructions", "7 Operation options"]
        ),
        None,
    )

    assert op_options is not None
    assert op_options.chunk_type == ChunkType.OPERATION_INSTRUCTION
    assert "12 seconds" in op_options.text


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
            if fragment.section_path == ["Ordering example"]
        ),
        None,
    )

    assert ordering_example is not None, (
        "Datasheet structured specs must activate for MANUAL-classified documents "
        "whose content contains 'ordering example'"
    )
    assert ordering_example.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
    assert "MK311007" in ordering_example.text


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
            if fragment.section_path == ["Final Inspection Report", "Device information"]
        ),
        None,
    )

    assert device_info is not None, (
        "Report structured specs must activate for MANUAL-classified documents "
        "whose title contains 'final inspection report'"
    )
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
            if f.section_path == ["Final Inspection Report", "Device information"]
        ),
        None,
    )

    assert device_info is not None, (
        "Report specs must activate via document_sections_combined_text even when "
        "document_title ('Pressure transmitter') contains no report marker"
    )
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
        (f for f in fragments if f.section_path == ["Ordering example"]),
        None,
    )

    assert ordering_example is not None, (
        "Datasheet specs must activate via document_sections_combined_text even when "
        "document_title ('DN25 DN80 MK311xxx') contains no datasheet marker"
    )
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
