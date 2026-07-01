from src.domain.common import ParserMetadata
from src.infrastructure.db.mappers import ElementMapper


def test_element_mapper_round_trip(sample_element) -> None:
    sample_element.parser_metadata = ParserMetadata(
        parser_name="docling",
        raw_source_type="text",
        raw_ref="#/pages/0/elements/1",
        extra={
            "markdown": "| Part | Value |",
            "caption": "Technical data",
            "ocr_text": "DF-100",
            "nearby_text": "Deck filler data",
        },
    )
    orm = ElementMapper.to_orm(sample_element)
    domain = ElementMapper.to_domain(orm)

    assert domain.element_id == sample_element.element_id
    assert domain.document_id == sample_element.document_id
    assert domain.element_type == sample_element.element_type
    assert domain.text == sample_element.text
    assert domain.parent_section_id == sample_element.parent_section_id
    assert domain.parser_metadata is not None
    assert domain.parser_metadata.raw_ref == "#/pages/0/elements/1"
    assert domain.parser_metadata.extra["markdown"] == "| Part | Value |"
    assert domain.parser_metadata.extra["ocr_text"] == "DF-100"
