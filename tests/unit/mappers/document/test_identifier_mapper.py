from src.infrastructure.db.mappers import IdentifierMapper


def test_identifier_mapper_round_trip(sample_identifier) -> None:
    orm = IdentifierMapper.to_orm(sample_identifier)
    domain = IdentifierMapper.to_domain(orm)

    assert domain.identifier_id == sample_identifier.identifier_id
    assert domain.document_id == sample_identifier.document_id
    assert domain.raw_value == sample_identifier.raw_value
    assert domain.normalized_value == sample_identifier.normalized_value
    assert domain.identifier_type == sample_identifier.identifier_type