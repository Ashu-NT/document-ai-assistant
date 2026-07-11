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

def test_returned_inference_contains_scores_reasons_and_statistics() -> None:
    result = infer_result(
        document_title="Pump Service Manual",
        sections=[make_section(section_id="sec_1", title="Maintenance Procedure")],
        elements={
            "sec_1": [
                make_element(
                    element_id="txt_1",
                    element_type=ElementType.TEXT,
                    text="Follow the maintenance procedure before operation.",
                ),
            ],
        },
    )

    assert isinstance(result.scores, dict)
    assert ChunkingProfile.MANUAL in result.scores
    assert isinstance(result.reasons[ChunkingProfile.MANUAL], list)
    assert result.statistics.manual_marker_hits >= 1
