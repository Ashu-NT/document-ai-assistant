from src.domain.common import DocumentType


def test_save_and_load_document_classification(
    db_uow,
    sample_document_classification,
) -> None:
    db_uow.classifications.save_document_classification(
        sample_document_classification
    )
    db_uow.commit()

    loaded = db_uow.classifications.get_document_classification(
        sample_document_classification.document_id
    )

    assert loaded is not None
    assert loaded.document_id == sample_document_classification.document_id
    assert loaded.document_type == DocumentType.MANUAL
    assert loaded.result.confidence_score > 0


def test_save_and_load_chunk_classification(
    db_uow,
    sample_chunk_classification,
) -> None:
    db_uow.classifications.save_chunk_classification(
        sample_chunk_classification
    )
    db_uow.commit()

    loaded = db_uow.classifications.get_chunk_classification(
        sample_chunk_classification.chunk_id
    )

    assert loaded is not None
    assert loaded.chunk_id == sample_chunk_classification.chunk_id
    assert loaded.result.predicted_label is not None


def test_list_chunk_classifications_by_document(
    db_uow,
    sample_chunk_classification,
) -> None:
    db_uow.classifications.save_chunk_classification(
        sample_chunk_classification
    )
    db_uow.commit()

    results = db_uow.classifications.list_chunk_classifications(
        sample_chunk_classification.document_id
    )

    assert len(results) == 1
    assert results[0].document_id == sample_chunk_classification.document_id


def test_document_classification_not_found_returns_none(
    db_uow,
) -> None:
    loaded = db_uow.classifications.get_document_classification(
        "does_not_exist"
    )

    assert loaded is None


def test_chunk_classification_not_found_returns_none(
    db_uow,
) -> None:
    loaded = db_uow.classifications.get_chunk_classification(
        "does_not_exist"
    )

    assert loaded is None