from src.infrastructure.db.mappers import ChunkVectorMapper


def test_chunk_vector_mapper_to_orm() -> None:
    orm = ChunkVectorMapper.to_orm(
        vector_id="vector_001",
        document_id="doc_001",
        chunk_id="chunk_001",
        qdrant_collection="document_chunks",
        qdrant_point_id="point_001",
        embedding_model="BAAI/bge-small-en-v1.5",
        embedding_text_hash="hash_001",
    )

    assert orm.id == "vector_001"
    assert orm.document_id == "doc_001"
    assert orm.chunk_id == "chunk_001"
    assert orm.qdrant_point_id == "point_001"
    assert orm.created_at is not None