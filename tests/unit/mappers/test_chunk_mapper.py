from src.infrastructure.db.mappers import ChunkMapper


def test_chunk_mapper_round_trip(sample_chunk) -> None:
    orm = ChunkMapper.to_orm(sample_chunk)
    domain = ChunkMapper.to_domain(
        orm,
        element_ids=sample_chunk.element_ids,
        table_ids=sample_chunk.table_ids,
        picture_ids=sample_chunk.picture_ids,
    )

    assert domain.chunk_id == sample_chunk.chunk_id
    assert domain.document_id == sample_chunk.document_id
    assert domain.content == sample_chunk.content
    assert domain.chunk_type == sample_chunk.chunk_type
    assert domain.section_path == sample_chunk.section_path