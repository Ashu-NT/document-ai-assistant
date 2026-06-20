from src.infrastructure.db.mappers import RetrievedChunkMapper ,ChunkMapper


def test_retrieved_chunk_mapper_from_chunk_orm(sample_chunk) -> None:
    chunk_orm = ChunkMapper.to_orm(sample_chunk)

    retrieved = RetrievedChunkMapper.from_chunk_orm(
        chunk_orm,
        score=0.8,
        retrieval_source="sql_keyword",
    )

    assert retrieved.chunk_id == sample_chunk.chunk_id
    assert retrieved.document_id == sample_chunk.document_id
    assert retrieved.score == 0.8
    assert retrieved.retrieval_source == "sql_keyword"
    assert retrieved.section_path == sample_chunk.section_path
