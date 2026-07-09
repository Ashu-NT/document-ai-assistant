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


def test_save_chunk_classifications_batch_round_trips(
    db_uow,
    sample_chunk_classification,
) -> None:
    db_uow.classifications.save_chunk_classifications([sample_chunk_classification])
    db_uow.commit()

    loaded = db_uow.classifications.get_chunk_classification(
        sample_chunk_classification.chunk_id
    )

    assert loaded is not None
    assert loaded.chunk_id == sample_chunk_classification.chunk_id


def test_save_chunk_classifications_batch_replaces_prior_row_for_same_chunk(
    db_uow,
    sample_chunk_classification,
) -> None:
    db_uow.classifications.save_chunk_classifications([sample_chunk_classification])
    db_uow.commit()

    reclassified = sample_chunk_classification.__class__(
        chunk_id=sample_chunk_classification.chunk_id,
        document_id=sample_chunk_classification.document_id,
        chunk_type=sample_chunk_classification.chunk_type,
        result=sample_chunk_classification.result.__class__(
            classification_id="classification_chunk_001_v2",
            document_id=sample_chunk_classification.document_id,
            predicted_label=sample_chunk_classification.chunk_type.value,
            confidence_score=0.42,
        ),
    )

    db_uow.classifications.save_chunk_classifications([reclassified])
    db_uow.commit()

    loaded = db_uow.classifications.get_chunk_classification(
        sample_chunk_classification.chunk_id
    )

    assert loaded is not None
    assert loaded.result.classification_id == "classification_chunk_001_v2"
    assert loaded.result.confidence_score == 0.42


def test_save_chunk_classifications_batch_is_noop_for_empty_list(
    db_uow,
) -> None:
    db_uow.classifications.save_chunk_classifications([])
    db_uow.commit()


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


def test_delete_document_classification_removes_the_row(
    db_uow,
    sample_document_classification,
) -> None:
    db_uow.classifications.save_document_classification(
        sample_document_classification
    )
    db_uow.commit()

    db_uow.classifications.delete_document_classification(
        sample_document_classification.document_id
    )
    db_uow.commit()

    assert (
        db_uow.classifications.get_document_classification(
            sample_document_classification.document_id
        )
        is None
    )


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