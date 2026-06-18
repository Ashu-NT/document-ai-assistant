import pytest

from src.infrastructure.db.orm_models import DocumentORM
from src.shared.exceptions import DatabaseError


def test_unit_of_work_commits_successfully(
    db_session,
    sample_document_graph,
    document_id,
) -> None:
    from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork

    with SqlAlchemyUnitOfWork(db_session) as uow:
        uow.documents.save_document_graph(sample_document_graph)

    saved = db_session.get(DocumentORM, document_id)

    assert saved is not None
    assert saved.id == document_id


def test_unit_of_work_rolls_back_on_error(
    db_session,
    sample_document_graph,
    document_id,
) -> None:
    from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork

    with pytest.raises(RuntimeError):
        with SqlAlchemyUnitOfWork(db_session) as uow:
            uow.documents.save_document_graph(sample_document_graph)
            raise RuntimeError("force rollback")

    saved = db_session.get(DocumentORM, document_id)

    assert saved is None


def test_unit_of_work_manual_commit(
    db_uow,
    db_session,
    sample_document_graph,
    document_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.commit()

    saved = db_session.get(DocumentORM, document_id)

    assert saved is not None


def test_unit_of_work_manual_rollback(
    db_uow,
    db_session,
    sample_document_graph,
    document_id,
) -> None:
    db_uow.documents.save_document_graph(sample_document_graph)
    db_uow.rollback()

    saved = db_session.get(DocumentORM, document_id)

    assert saved is None