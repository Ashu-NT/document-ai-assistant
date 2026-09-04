from src.application.workflows.ingestion.models.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.pipeline.stage_lifecycle.ingestion_stage_lifecycle_coordinator import (
    IngestionStageLifecycleCoordinator,
)
from src.domain.workflow import IngestionRun

_LOGGER_NAME = (
    "src.application.workflows.ingestion.pipeline.stage_lifecycle"
    ".ingestion_stage_lifecycle_coordinator"
)


class _FakeRunStore:
    def mark_status(self, ingestion_run, status) -> None:
        pass


class _FakeEventPublisher:
    def publish_stage_started(self, **kwargs) -> None:
        pass

    def publish_stage_completed(self, **kwargs) -> None:
        pass


def _make_coordinator() -> IngestionStageLifecycleCoordinator:
    return IngestionStageLifecycleCoordinator(
        run_store=_FakeRunStore(), event_publisher=_FakeEventPublisher()
    )


def _make_session() -> tuple:
    ingestion_run = IngestionRun(run_id="run_1", document_id="doc_1")
    coordinator = _make_coordinator()
    session = coordinator.create_session(
        ingestion_run=ingestion_run, file_name="manual.pdf", event_context=None
    )
    return coordinator, session


def test_complete_logs_stage_duration_and_payload_counts(caplog) -> None:
    coordinator, session = _make_session()

    with caplog.at_level("INFO", logger=_LOGGER_NAME):
        coordinator.start(session, stage=IngestionStage.REGISTRATION)
        coordinator.complete(
            session,
            stage=IngestionStage.REGISTRATION,
            payload={"chunk_count": 12, "nested": {"should": "be dropped"}},
        )

    assert len(caplog.records) == 1
    message = caplog.records[0].getMessage()
    assert "stage=registration" in message
    assert "status=ok" in message
    assert "document_id=doc_1" in message
    assert "ingestion_run_id=run_1" in message
    assert "chunk_count=12" in message
    assert "nested" not in message


def test_complete_without_a_matching_start_does_not_log_or_crash(caplog) -> None:
    coordinator, session = _make_session()

    with caplog.at_level("INFO", logger=_LOGGER_NAME):
        coordinator.complete(session, stage=IngestionStage.CLASSIFICATION)

    assert caplog.records == []


def test_start_then_complete_of_a_different_stage_does_not_log_the_wrong_one(
    caplog,
) -> None:
    coordinator, session = _make_session()

    with caplog.at_level("INFO", logger=_LOGGER_NAME):
        coordinator.start(session, stage=IngestionStage.REGISTRATION)
        coordinator.complete(session, stage=IngestionStage.CLASSIFICATION)

    assert caplog.records == []
    # the still-open REGISTRATION start time survives for its own complete()
    assert IngestionStage.REGISTRATION in session.stage_started_at
