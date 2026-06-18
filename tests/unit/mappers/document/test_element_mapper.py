from src.infrastructure.db.mappers import ElementMapper


def test_element_mapper_round_trip(sample_element) -> None:
    orm = ElementMapper.to_orm(sample_element)
    domain = ElementMapper.to_domain(orm)

    assert domain.element_id == sample_element.element_id
    assert domain.document_id == sample_element.document_id
    assert domain.element_type == sample_element.element_type
    assert domain.text == sample_element.text
    assert domain.parent_section_id == sample_element.parent_section_id