from datetime import datetime, timezone

from src.domain.common import IngestionStatus


def test_ingestion_run_can_mark_running(sample_ingestion_run) -> None:
    now = datetime.now(timezone.utc)

    sample_ingestion_run.mark_running(now)

    assert sample_ingestion_run.status == IngestionStatus.RUNNING
    assert sample_ingestion_run.started_at == now


def test_ingestion_run_can_mark_success(sample_ingestion_run) -> None:
    now = datetime.now(timezone.utc)

    sample_ingestion_run.mark_success(now)

    assert sample_ingestion_run.status == IngestionStatus.SUCCESS
    assert sample_ingestion_run.finished_at == now
    assert sample_ingestion_run.error_message is None


def test_ingestion_run_can_mark_failed(sample_ingestion_run) -> None:
    now = datetime.now(timezone.utc)

    sample_ingestion_run.mark_failed(
        finished_at=now,
        error_message="Docling parse failed",
    )

    assert sample_ingestion_run.status == IngestionStatus.FAILED
    assert sample_ingestion_run.finished_at == now
    assert sample_ingestion_run.error_message == "Docling parse failed"


def test_ingestion_run_can_mark_file_duplicate(sample_ingestion_run) -> None:
    now = datetime.now(timezone.utc)

    sample_ingestion_run.mark_file_duplicate(now)

    assert sample_ingestion_run.status == IngestionStatus.SKIPPED_FILE_DUPLICATE
    assert sample_ingestion_run.finished_at == now


def test_ingestion_run_can_mark_content_duplicate(sample_ingestion_run) -> None:
    now = datetime.now(timezone.utc)

    sample_ingestion_run.mark_content_duplicate(now)

    assert sample_ingestion_run.status == IngestionStatus.SKIPPED_CONTENT_DUPLICATE
    assert sample_ingestion_run.finished_at == now