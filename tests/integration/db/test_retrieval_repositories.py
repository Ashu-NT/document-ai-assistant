from src.infrastructure.db.repositories.retrieval import (
    SqlAlchemyVectorMappingRepository,
    SqlKeywordRepository,
)


def test_vector_mapping_repository_saves_and_gets_qdrant_point_id(
    db_uow,
    db_session,
    sample_document_graph,
    document_id,
    chunk_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    repository = SqlAlchemyVectorMappingRepository(db_session)

    repository.save_mapping(
        vector_id="vector_001",
        document_id=document_id,
        chunk_id=chunk_id,
        qdrant_collection="document_chunks",
        qdrant_point_id="qdrant_point_001",
        embedding_model="BAAI/bge-small-en-v1.5",
        embedding_text_hash="hash_001",
    )
    db_session.commit()

    point_id = repository.get_qdrant_point_id(chunk_id)

    assert point_id == "qdrant_point_001"


def test_vector_mapping_repository_lists_chunk_ids_by_document(
    db_uow,
    db_session,
    sample_document_graph,
    document_id,
    chunk_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    repository = SqlAlchemyVectorMappingRepository(db_session)

    repository.save_mapping(
        vector_id="vector_001",
        document_id=document_id,
        chunk_id=chunk_id,
        qdrant_collection="document_chunks",
        qdrant_point_id="qdrant_point_001",
        embedding_model="BAAI/bge-small-en-v1.5",
    )
    db_session.commit()

    chunk_ids = repository.list_chunk_ids_by_document(document_id)

    assert chunk_ids == [chunk_id]


def test_sql_keyword_repository_searches_chunks(
    db_uow,
    db_session,
    sample_document_graph,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    repository = SqlKeywordRepository(db_session)

    results = repository.search_chunks(
        query="hydraulic filter",
        limit=5,
    )

    assert len(results) == 1
    assert results[0].chunk_id == "chunk_001"
    assert results[0].retrieval_source == "sql_keyword"