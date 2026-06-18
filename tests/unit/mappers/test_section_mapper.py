from src.infrastructure.db.mappers import SectionMapper


def test_section_mapper_round_trip(sample_section) -> None:
    orm = SectionMapper.to_orm(sample_section)
    domain = SectionMapper.to_domain(orm, element_ids=sample_section.element_ids)

    assert domain.section_id == sample_section.section_id
    assert domain.document_id == sample_section.document_id
    assert domain.title == sample_section.title
    assert domain.section_path == sample_section.section_path
    assert domain.element_ids == sample_section.element_ids