import pytest

from src.domain.common import DocumentType

# document_classifications.document_id is now a CASCADE FK to documents.id
# (real enforcement only started once the test engine's PRAGMA gap was
# fixed), so a real "doc_001" row must exist before these tests can insert.
pytestmark = pytest.mark.usefixtures("seeded_document_and_chunk")


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