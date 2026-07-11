from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_inference import (
    ChunkingProfileInference,
)

from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)

from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_inferer import (
    ChunkingProfileInferer,
)

from src.domain.common import ElementType

from src.domain.document import DocumentSection

from src.domain.elements import CanonicalElement

def make_section(
    *,
    section_id: str,
    title: str,
    level: int = 1,
    parent_section_id: str | None = None,
    section_path: list[str] | None = None,
) -> DocumentSection:
    return DocumentSection(
        section_id=section_id,
        document_id="doc_001",
        title=title,
        level=level,
        parent_section_id=parent_section_id,
        section_path=section_path or [title],
    )

def make_element(
    *,
    element_id: str,
    element_type: ElementType,
    text: str | None = None,
    ) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
    )

def infer_result(
    *,
    document_title: str,
    sections: list[DocumentSection],
    elements: dict[str, list[CanonicalElement]],
) -> ChunkingProfileInference:
    inferer = ChunkingProfileInferer()
    return inferer.infer_result(
        document_title=document_title,
        sections=sections,
        section_elements_by_id=elements,
    )

def test_manual_like_document_selects_manual_with_reasons() -> None:
    sections = [
        make_section(
            section_id="sec_root",
            title="Maintenance Procedure",
            section_path=["Maintenance Procedure"],
        ),
        make_section(
            section_id="sec_child",
            title="Troubleshooting Steps",
            level=2,
            parent_section_id="sec_root",
            section_path=["Maintenance Procedure", "Troubleshooting Steps"],
        ),
    ]
    result = infer_result(
        document_title="Hydraulic Pump Service Manual",
        sections=sections,
        elements={
            "sec_root": [
                make_element(
                    element_id="el_001",
                    element_type=ElementType.TEXT,
                    text="Follow the maintenance procedure carefully before servicing the pump assembly.",
                ),
                make_element(
                    element_id="el_002",
                    element_type=ElementType.LIST_ITEM,
                    text="Disconnect power and isolate the hydraulic circuit.",
                ),
            ],
            "sec_child": [
                make_element(
                    element_id="el_003",
                    element_type=ElementType.TEXT,
                    text="Use the troubleshooting checklist to inspect filters, seals, and pressure levels.",
                ),
                make_element(
                    element_id="el_004",
                    element_type=ElementType.LIST_ITEM,
                    text="Record findings and continue with the repair task.",
                ),
            ],
        },
    )

    assert result.selected_profile == ChunkingProfile.MANUAL
    assert any(
        "manual markers" in reason.lower()
        for reason in result.reasons[ChunkingProfile.MANUAL]
    )

def test_datasheet_like_document_selects_datasheet_with_reasons() -> None:
    result = infer_result(
        document_title="ADC Converter Datasheet",
        sections=[make_section(section_id="sec_specs", title="Electrical Specifications")],
        elements={
            "sec_specs": [
                make_element(element_id="el_001", element_type=ElementType.TABLE),
                make_element(element_id="el_002", element_type=ElementType.TABLE),
                make_element(
                    element_id="el_003",
                    element_type=ElementType.TEXT,
                    text="Voltage current tolerance range.",
                ),
            ]
        },
    )

    assert result.selected_profile == ChunkingProfile.DATASHEET
    assert any(
        "datasheet/specification markers" in reason.lower()
        for reason in result.reasons[ChunkingProfile.DATASHEET]
    )

def test_drawing_like_document_selects_drawing_with_reasons() -> None:
    result = infer_result(
        document_title="Main Wiring Diagram",
        sections=[make_section(section_id="sec_draw", title="Schematic Layout")],
        elements={
            "sec_draw": [
                make_element(element_id="pic_001", element_type=ElementType.PICTURE),
                make_element(element_id="cap_001", element_type=ElementType.CAPTION, text="Figure 1"),
                make_element(element_id="pic_002", element_type=ElementType.PICTURE),
                make_element(element_id="cap_002", element_type=ElementType.CAPTION, text="Figure 2"),
                make_element(
                    element_id="txt_001",
                    element_type=ElementType.TEXT,
                    text="Terminal labels only.",
                ),
            ]
        },
    )

    assert result.selected_profile == ChunkingProfile.DRAWING
    assert any(
        "drawing/schematic markers" in reason.lower()
        or "pictures are dominant" in reason.lower()
        for reason in result.reasons[ChunkingProfile.DRAWING]
    )

def test_report_like_document_selects_report_with_reasons() -> None:
    sections = [
        make_section(section_id="sec_1", title="Abstract"),
        make_section(section_id="sec_2", title="Methodology"),
        make_section(section_id="sec_3", title="Results"),
        make_section(section_id="sec_4", title="Discussion"),
    ]
    result = infer_result(
        document_title="Field Study Report",
        sections=sections,
        elements={
            "sec_1": [
                make_element(
                    element_id="txt_1",
                    element_type=ElementType.TEXT,
                    text="This report summarizes the background, scope, and objective of the field study in detail.",
                ),
            ],
            "sec_2": [
                make_element(
                    element_id="txt_2",
                    element_type=ElementType.TEXT,
                    text="The methodology section explains sampling, instrumentation, and evaluation criteria used in the study.",
                ),
            ],
            "sec_3": [
                make_element(
                    element_id="txt_3",
                    element_type=ElementType.TEXT,
                    text="Results show a measurable reduction in vibration and improved signal stability after the intervention.",
                ),
            ],
            "sec_4": [
                make_element(
                    element_id="txt_4",
                    element_type=ElementType.TEXT,
                    text="The discussion evaluates limitations, compares outcomes, and motivates the conclusion of the report.",
                ),
            ],
        },
    )

    assert result.selected_profile == ChunkingProfile.REPORT
    assert any(
        "report markers" in reason.lower()
        for reason in result.reasons[ChunkingProfile.REPORT]
    )

def test_weak_ambiguous_document_selects_default() -> None:
    result = infer_result(
        document_title="General Notes",
        sections=[make_section(section_id="sec_1", title="Overview")],
        elements={
            "sec_1": [
                make_element(
                    element_id="txt_1",
                    element_type=ElementType.TEXT,
                    text="General notes for internal circulation.",
                ),
            ]
        },
    )

    assert result.selected_profile == ChunkingProfile.DEFAULT
    assert any(
        "weak" in reason.lower() or "ambiguous" in reason.lower()
        for reason in result.reasons[ChunkingProfile.DEFAULT]
    )

def test_logo_heavy_but_text_rich_document_does_not_select_drawing() -> None:
    result = infer_result(
        document_title="Pump Service Guide",
        sections=[
            make_section(section_id="sec_1", title="Procedure"),
            make_section(section_id="sec_2", title="Troubleshooting"),
        ],
        elements={
            "sec_1": [
                make_element(element_id="pic_1", element_type=ElementType.PICTURE),
                make_element(element_id="pic_2", element_type=ElementType.PICTURE),
                make_element(
                    element_id="txt_1",
                    element_type=ElementType.TEXT,
                    text="The service procedure explains inspection, maintenance, and installation steps for the pump system.",
                ),
                make_element(
                    element_id="txt_2",
                    element_type=ElementType.TEXT,
                    text="Each step includes safety cautions, operational checks, and verification notes for technicians.",
                ),
            ],
            "sec_2": [
                make_element(element_id="pic_3", element_type=ElementType.PICTURE),
                make_element(
                    element_id="txt_3",
                    element_type=ElementType.TEXT,
                    text="Troubleshooting guidance covers pressure loss, flow instability, and seal wear in detail.",
                ),
            ],
        },
    )

    assert result.selected_profile != ChunkingProfile.DRAWING
