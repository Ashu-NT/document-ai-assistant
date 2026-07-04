from __future__ import annotations

from types import SimpleNamespace

from src.application.orchestrator.ingestion.ingestion_runtime import IngestionRuntime


def _make_runtime(*, unit_of_work, qdrant_client=None) -> IngestionRuntime:
    placeholder = object()
    return IngestionRuntime(
        ingestion_workflow=placeholder,
        delete_document_workflow=placeholder,
        parsing_workflow=placeholder,
        document_graph_builder=placeholder,
        document_registration_service=placeholder,
        document_lookup_service=placeholder,
        duplicate_detection_service=placeholder,
        classification_service=placeholder,
        document_classification_workflow=placeholder,
        post_classification_chunk_finalization_workflow=placeholder,
        unit_of_work=unit_of_work,
        embedding_model="bge-small",
        vector_collection="document_chunks",
        qdrant_client=qdrant_client,
    )


def test_close_closes_session_and_qdrant_client():
    closed = {"session": False, "client": False}
    session = SimpleNamespace(close=lambda: closed.__setitem__("session", True))
    uow = SimpleNamespace(session=session)
    client = SimpleNamespace(close=lambda: closed.__setitem__("client", True))

    runtime = _make_runtime(unit_of_work=uow, qdrant_client=client)
    runtime.close()

    assert closed == {"session": True, "client": True}


def test_close_tolerates_missing_qdrant_client():
    session = SimpleNamespace(close=lambda: None)
    uow = SimpleNamespace(session=session)

    runtime = _make_runtime(unit_of_work=uow, qdrant_client=None)

    runtime.close()  # must not raise


def test_close_tolerates_missing_session():
    uow = SimpleNamespace()  # no `session` attribute at all

    runtime = _make_runtime(unit_of_work=uow, qdrant_client=None)

    runtime.close()  # must not raise


def test_close_swallows_qdrant_client_close_errors():
    session = SimpleNamespace(close=lambda: None)
    uow = SimpleNamespace(session=session)

    def _raise():
        raise RuntimeError("boom")

    client = SimpleNamespace(close=_raise)
    runtime = _make_runtime(unit_of_work=uow, qdrant_client=client)

    runtime.close()  # must not raise
