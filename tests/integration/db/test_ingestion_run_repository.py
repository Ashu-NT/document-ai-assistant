from datetime import datetime, timezone

from src.domain.common import IngestionStatus


def test_ingestion_run_repository_create_and_get(
    db_uow,
    sample_ingestion_run,
) -> None:
    db_uow.ingestion_runs.create(sample_ingestion_run)
    db_uow.commit()

    loaded = db_uow.ingestion_runs.get(sample_ingestion_run.run_id)

    assert loaded is not None
    assert loaded.run_id == sample_ingestion_run.run_id
    assert loaded.file_hash == sample_ingestion_run.file_hash


def test_ingestion_run_repository_update(
    db_uow,
    sample_ingestion_run,
) -> None:
    db_uow.ingestion_runs.create(sample_ingestion_run)
    db_uow.commit()

    now = datetime.now(timezone.utc)
    sample_ingestion_run.mark_running(now)

    db_uow.ingestion_runs.update(sample_ingestion_run)
    db_uow.commit()

    loaded = db_uow.ingestion_runs.get(sample_ingestion_run.run_id)

    assert loaded is not None
    assert loaded.status == IngestionStatus.RUNNING


def test_ingestion_run_repository_mark_status(
    db_uow,
    sample_ingestion_run,
) -> None:
    db_uow.ingestion_runs.create(sample_ingestion_run)
    db_uow.commit()

    db_uow.ingestion_runs.mark_status(
        sample_ingestion_run.run_id,
        IngestionStatus.FAILED,
        error_message="parse failed",
    )
    db_uow.commit()

    loaded = db_uow.ingestion_runs.get(sample_ingestion_run.run_id)

    assert loaded is not None
    assert loaded.status == IngestionStatus.FAILED
    assert loaded.error_message == "parse failed"