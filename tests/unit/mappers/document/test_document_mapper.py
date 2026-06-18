from src.infrastructure.db.mappers import DocumentMapper


def test_document_mapper_round_trip(sample_document) -> None:
    orm = DocumentMapper.to_orm(sample_document)
    domain = DocumentMapper.to_domain(orm)

    assert domain.document_id == sample_document.document_id
    assert domain.file_name == sample_document.file_name
    assert domain.hashes.file_hash == sample_document.hashes.file_hash
    assert domain.document_type == sample_document.document_type