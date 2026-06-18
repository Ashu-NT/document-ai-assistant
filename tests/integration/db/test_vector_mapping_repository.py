def test_list_qdrant_point_ids_by_document(
    db_uow,
) -> None:
    db_uow.vector_mappings.save_mapping(
        vector_id="vector_001",
        document_id="doc_001",
        chunk_id="chunk_001",
        qdrant_collection="document_chunks",
        qdrant_point_id="point_001",
        embedding_model="bge-small",
    )

    db_uow.vector_mappings.save_mapping(
        vector_id="vector_002",
        document_id="doc_001",
        chunk_id="chunk_002",
        qdrant_collection="document_chunks",
        qdrant_point_id="point_002",
        embedding_model="bge-small",
    )

    db_uow.commit()

    point_ids = (
        db_uow.vector_mappings
        .list_qdrant_point_ids_by_document("doc_001")
    )

    assert len(point_ids) == 2
    assert "point_001" in point_ids
    assert "point_002" in point_ids
    
def test_delete_document_mappings(
    db_uow,
) -> None:
    db_uow.vector_mappings.save_mapping(
        vector_id="vector_001",
        document_id="doc_001",
        chunk_id="chunk_001",
        qdrant_collection="document_chunks",
        qdrant_point_id="point_001",
        embedding_model="bge-small",
    )

    db_uow.vector_mappings.save_mapping(
        vector_id="vector_002",
        document_id="doc_001",
        chunk_id="chunk_002",
        qdrant_collection="document_chunks",
        qdrant_point_id="point_002",
        embedding_model="bge-small",
    )

    db_uow.commit()

    db_uow.vector_mappings.delete_document_mappings("doc_001")
    db_uow.commit()

    point_ids = db_uow.vector_mappings.list_qdrant_point_ids_by_document(
        "doc_001"
    )

    assert point_ids == []