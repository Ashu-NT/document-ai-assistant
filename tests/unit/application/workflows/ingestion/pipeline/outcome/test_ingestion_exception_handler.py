import pytest

from src.application.workflows.ingestion.models.ingestion_exceptions import (
    IngestionWorkflowError,
)
from src.application.workflows.ingestion.models.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.pipeline.outcome.ingestion_exception_handler import (
    IngestionExceptionHandler,
)
from src.domain.common import IngestionStatus
from src.domain.workflow import IngestionRun
from src.shared.exceptions import DatabaseError
from src.shared.ids import IdGenerator


class FakeRunStore:
    def __init__(self, *, fail_first_update_with_document_id: bool = False) -> None:
        self.fail_first_update_with_document_id = fail_first_update_with_document_id
        self.rollback_calls = 0
        self.update_calls: list[str | None] = []

    def rollback(self) -> None:
        self.rollback_calls += 1

    def update(self, ingestion_run: IngestionRun) -> None:
        self.update_calls.append(ingestion_run.document_id)
        if (
            self.fail_first_update_with_document_id
            and len(self.update_calls) == 1
            and ingestion_run.document_id is not None
        ):
            raise DatabaseError("Failed to commit database transaction.")


class FakeEventPublisher:
    def __init__(self) -> None:
        self.published_events = []
        self.published_event_contexts = []

    def publish_event(self, event, *, event_context=None) -> None:
        self.published_events.append(event)
        self.published_event_contexts.append(event_context)


def _make_handler(run_store: FakeRunStore) -> tuple[IngestionExceptionHandler, FakeEventPublisher]:
    event_publisher = FakeEventPublisher()
    handler = IngestionExceptionHandler(
        run_store=run_store,
        id_generator=IdGenerator(),
        event_publisher=event_publisher,
    )
    return handler, event_publisher


def test_handle_records_failure_normally_when_document_id_is_valid() -> None:
    run_store = FakeRunStore(fail_first_update_with_document_id=False)
    handler, event_publisher = _make_handler(run_store)
    ingestion_run = IngestionRun(run_id="run_1", document_id="doc_1")

    with pytest.raises(IngestionWorkflowError):
        handler.handle(
            RuntimeError("boom"),
            ingestion_run=ingestion_run,
            current_stage=IngestionStage.REGISTRATION,
            file_path="/tmp/doc.pdf",
            file_name="doc.pdf",
            event_context=None,
        )

    assert run_store.rollback_calls == 1
    assert run_store.update_calls == ["doc_1"]
    assert ingestion_run.document_id == "doc_1"
    assert ingestion_run.status == IngestionStatus.FAILED
    assert event_publisher.published_events[0].document_id == "doc_1"


def test_handle_clears_document_id_and_retries_when_update_hits_fk_violation() -> None:
    run_store = FakeRunStore(fail_first_update_with_document_id=True)
    handler, event_publisher = _make_handler(run_store)
    ingestion_run = IngestionRun(run_id="run_1", document_id="doc_rolled_back")

    with pytest.raises(IngestionWorkflowError):
        handler.handle(
            RuntimeError("Failed to save document graph."),
            ingestion_run=ingestion_run,
            current_stage=IngestionStage.REGISTRATION,
            file_path="/tmp/doc.pdf",
            file_name="doc.pdf",
            event_context=None,
        )

    assert run_store.rollback_calls == 1
    # First attempt used the original (now-dangling) document_id and raised;
    # the retry used None and succeeded.
    assert run_store.update_calls == ["doc_rolled_back", None]
    assert ingestion_run.document_id is None
    assert ingestion_run.status == IngestionStatus.FAILED
    # The event still carries the original document_id for diagnostics, even
    # though the persisted ingestion_run row no longer references it.
    assert event_publisher.published_events[0].document_id == "doc_rolled_back"
