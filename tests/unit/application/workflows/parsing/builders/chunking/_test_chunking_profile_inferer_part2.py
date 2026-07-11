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

def test_manual_with_many_tables_does_not_select_datasheet_if_manual_markers_are_strong() -> None:
    result = infer_result(
        document_title="Field Service Manual",
        sections=[
            make_section(section_id="sec_1", title="Maintenance Procedure"),
            make_section(
                section_id="sec_2",
                title="Installation Task",
                level=2,
                parent_section_id="sec_1",
                section_path=["Maintenance Procedure", "Installation Task"],
            ),
        ],
        elements={
            "sec_1": [
                make_element(element_id="tbl_1", element_type=ElementType.TABLE),
                make_element(element_id="tbl_2", element_type=ElementType.TABLE),
                make_element(
                    element_id="txt_1",
                    element_type=ElementType.TEXT,
                    text="This maintenance procedure explains when and how to service the hydraulic control assembly safely.",
                ),
                make_element(
                    element_id="lst_1",
                    element_type=ElementType.LIST_ITEM,
                    text="Inspect filters, replace seals, and verify operating pressure.",
                ),
            ],
            "sec_2": [
                make_element(element_id="tbl_3", element_type=ElementType.TABLE),
                make_element(
                    element_id="txt_2",
                    element_type=ElementType.TEXT,
                    text="Installation steps must be completed in sequence before returning the pump to operation.",
                ),
            ],
        },
    )

    assert result.selected_profile == ChunkingProfile.MANUAL
    assert (
        result.scores[ChunkingProfile.MANUAL]
        > result.scores[ChunkingProfile.DATASHEET]
    )

def test_confidence_is_higher_when_top_score_strongly_beats_second() -> None:
    strong_result = infer_result(
        document_title="Precision Wiring Diagram",
        sections=[make_section(section_id="sec_1", title="Schematic Layout")],
        elements={
            "sec_1": [
                make_element(element_id="pic_1", element_type=ElementType.PICTURE),
                make_element(element_id="pic_2", element_type=ElementType.PICTURE),
                make_element(element_id="cap_1", element_type=ElementType.CAPTION, text="Figure A"),
                make_element(element_id="cap_2", element_type=ElementType.CAPTION, text="Figure B"),
                make_element(
                    element_id="txt_1",
                    element_type=ElementType.TEXT,
                    text="Pin labels only.",
                ),
            ],
        },
    )
    close_result = infer_result(
        document_title="Service Specification Notes",
        sections=[
            make_section(section_id="sec_1", title="Maintenance Specifications"),
            make_section(section_id="sec_2", title="Procedure Notes"),
        ],
        elements={
            "sec_1": [
                make_element(element_id="tbl_1", element_type=ElementType.TABLE),
                make_element(
                    element_id="txt_1",
                    element_type=ElementType.TEXT,
                    text="Specification values are listed for each configurable pressure setting.",
                ),
            ],
            "sec_2": [
                make_element(
                    element_id="txt_2",
                    element_type=ElementType.TEXT,
                    text="Procedure notes describe how technicians should verify those values during maintenance.",
                ),
                make_element(
                    element_id="lst_1",
                    element_type=ElementType.LIST_ITEM,
                    text="Record service values after inspection.",
                ),
            ],
        },
    )

    assert strong_result.confidence > close_result.confidence
    assert strong_result.confidence >= 0.75

def test_confidence_is_low_when_top_two_scores_are_close() -> None:
    result = infer_result(
        document_title="Maintenance Specification Overview",
        sections=[
            make_section(section_id="sec_1", title="Maintenance Specifications"),
            make_section(section_id="sec_2", title="Procedure Summary"),
        ],
        elements={
            "sec_1": [
                make_element(element_id="tbl_1", element_type=ElementType.TABLE),
                make_element(
                    element_id="txt_1",
                    element_type=ElementType.TEXT,
                    text="Specification values define pressure, flow, and temperature boundaries for operation.",
                ),
            ],
            "sec_2": [
                make_element(
                    element_id="txt_2",
                    element_type=ElementType.TEXT,
                    text="Procedure guidance explains how to inspect those values during maintenance service tasks.",
                ),
                make_element(
                    element_id="lst_1",
                    element_type=ElementType.LIST_ITEM,
                    text="Verify limits, document readings, and continue with the task.",
                ),
            ],
        },
    )

    ordered_scores = sorted(result.scores.values(), reverse=True)

    assert ordered_scores[0] - ordered_scores[1] < 1.5
    assert result.confidence <= 0.65

def test_certificate_like_document_selects_certificate_with_reasons() -> None:
    result = infer_result(
        document_title="Inspection Certificate",
        sections=[
            make_section(section_id="sec_1", title="General Information"),
            make_section(section_id="sec_2", title="Particulars"),
            make_section(section_id="sec_3", title="Test Certificate"),
        ],
        elements={
            "sec_1": [
                make_element(element_id="tbl_1", element_type=ElementType.TABLE),
                make_element(
                    element_id="txt_1",
                    element_type=ElementType.TEXT,
                    text="Certificate number: CERT-2024-00312",
                ),
            ],
            "sec_2": [
                make_element(element_id="tbl_2", element_type=ElementType.TABLE),
                make_element(
                    element_id="txt_2",
                    element_type=ElementType.TEXT,
                    text="Serial number: DN50-001",
                ),
            ],
            "sec_3": [
                make_element(element_id="tbl_3", element_type=ElementType.TABLE),
                make_element(
                    element_id="txt_3",
                    element_type=ElementType.TEXT,
                    text="Test pressure: 10 bar",
                ),
            ],
        },
    )

    assert result.selected_profile == ChunkingProfile.CERTIFICATE
    assert any(
        "certificate markers" in reason.lower()
        for reason in result.reasons[ChunkingProfile.CERTIFICATE]
    )

def test_certificate_marker_hits_are_counted_in_statistics() -> None:
    result = infer_result(
        document_title="Certificate of Conformity",
        sections=[make_section(section_id="sec_1", title="Conformity Statement")],
        elements={
            "sec_1": [
                make_element(
                    element_id="txt_1",
                    element_type=ElementType.TEXT,
                    text="This certificate confirms conformity with the applicable standards.",
                ),
            ]
        },
    )

    assert result.statistics.certificate_marker_hits >= 1

def test_certificate_profile_does_not_select_for_manual_heavy_document() -> None:
    result = infer_result(
        document_title="Maintenance Manual",
        sections=[
            make_section(section_id="sec_1", title="Maintenance Procedure"),
            make_section(section_id="sec_2", title="Installation Task", level=2, parent_section_id="sec_1"),
            make_section(section_id="sec_3", title="Troubleshooting"),
        ],
        elements={
            "sec_1": [
                make_element(
                    element_id="txt_1",
                    element_type=ElementType.TEXT,
                    text="Follow the maintenance procedure carefully before servicing the pump.",
                ),
                make_element(element_id="lst_1", element_type=ElementType.LIST_ITEM, text="Isolate power."),
                make_element(element_id="lst_2", element_type=ElementType.LIST_ITEM, text="Replace seals."),
            ],
            "sec_2": [
                make_element(
                    element_id="txt_2",
                    element_type=ElementType.TEXT,
                    text="Installation steps must be completed in sequence per the service manual.",
                ),
            ],
            "sec_3": [
                make_element(
                    element_id="txt_3",
                    element_type=ElementType.TEXT,
                    text="Troubleshooting guidance covers common faults and their remedies.",
                ),
            ],
        },
    )

    assert result.selected_profile != ChunkingProfile.CERTIFICATE
