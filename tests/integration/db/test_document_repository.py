def test_document_repository_saves_and_loads_document_graph(
    db_uow,
    sample_document_graph,
    document_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    loaded = db_uow.documents.get_document_graph(document_id)

    assert loaded is not None
    assert loaded.document.document_id == document_id
    assert len(loaded.sections) == 1
    assert len(loaded.elements) == 1
    assert len(loaded.chunks) == 1
    assert len(loaded.questions) == 1
    assert len(loaded.identifiers) == 1


def test_document_repository_finds_duplicate_by_file_hash(
    db_uow,
    sample_document_graph,
    sample_document,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    found_document_id = db_uow.documents.find_document_id_by_file_hash(
        sample_document.hashes.file_hash,
    )

    assert found_document_id == sample_document.document_id


def test_document_repository_finds_duplicate_by_content_hash(
    db_uow,
    sample_document_graph,
    sample_document,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    found_document_id = db_uow.documents.find_document_id_by_content_hash(
        sample_document.hashes.content_hash,
    )

    assert found_document_id == sample_document.document_id


def test_document_repository_lists_chunks_by_document(
    db_uow,
    sample_document_graph,
    document_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    chunks = db_uow.documents.list_chunks_by_document(document_id)

    assert len(chunks) == 1
    assert chunks[0].document_id == document_id


def test_document_repository_gets_chunks_by_ids(
    db_uow,
    sample_document_graph,
    chunk_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    chunks = db_uow.documents.get_chunks_by_ids([chunk_id])

    assert len(chunks) == 1
    assert chunks[0].chunk_id == chunk_id


def test_document_repository_searches_identifiers(
    db_uow,
    sample_document_graph,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    identifiers = db_uow.documents.search_identifiers("HP-001")

    assert len(identifiers) == 1
    assert identifiers[0].raw_value.strip() == "HP-001"