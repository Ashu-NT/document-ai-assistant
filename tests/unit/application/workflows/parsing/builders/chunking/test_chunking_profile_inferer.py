from src.application.workflows.parsing.builders.chunking.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.chunking_profile_inferer import (
    ChunkingProfileInferer,
)
from src.domain.common import ElementType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


def make_section(*, section_id: str, title: str) -> DocumentSection:
    return DocumentSection(
        section_id=section_id,
        document_id="doc_001",
        title=title,
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


def test_inferer_returns_datasheet_profile_for_table_heavy_document() -> None:
    inferer = ChunkingProfileInferer()
    sections = [make_section(section_id="sec_specs", title="Electrical Specifications")]
    elements = {
        "sec_specs": [
            make_element(element_id="el_001", element_type=ElementType.TABLE),
            make_element(element_id="el_002", element_type=ElementType.TABLE),
            make_element(
                element_id="el_003",
                element_type=ElementType.TEXT,
                text="Voltage current tolerance range.",
            ),
        ]
    }

    profile = inferer.infer(
        document_title="ADC Converter Datasheet",
        sections=sections,
        section_elements_by_id=elements,
    )

    assert profile == ChunkingProfile.DATASHEET
