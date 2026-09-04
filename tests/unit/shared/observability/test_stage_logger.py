import logging

import pytest

from src.shared.observability.stage_logger import log_stage_result, time_stage


def test_log_stage_result_formats_fixed_fields_and_counts() -> None:
    logger = logging.getLogger("test.stage_logger.fixed_fields")

    with pytest.MonkeyPatch.context() as mp:
        records = []
        mp.setattr(logger, "log", lambda level, fmt, *args: records.append((level, fmt % args)))
        log_stage_result(
            logger,
            stage_name="my_stage",
            duration_ms=12.345,
            status="ok",
            document_id="doc_1",
            ingestion_run_id="run_1",
            counts={"chunks": 3, "tables": 0},
        )

    assert len(records) == 1
    level, message = records[0]
    assert level == logging.INFO
    assert "stage=my_stage" in message
    assert "duration_ms=12.3" in message
    assert "status=ok" in message
    assert "document_id=doc_1" in message
    assert "ingestion_run_id=run_1" in message
    assert "chunks=3" in message
    assert "tables=0" in message


def test_log_stage_result_fixed_fields_win_over_colliding_count_keys() -> None:
    """A caller-supplied counts dict containing a key that collides with a
    fixed field name (e.g. GraphBuildStageScope.output_counts["document_id"])
    must never silently override the real document_id, nor crash."""
    logger = logging.getLogger("test.stage_logger.collision")
    records = []
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(logger, "log", lambda level, fmt, *args: records.append(fmt % args))
        log_stage_result(
            logger,
            stage_name="my_stage",
            duration_ms=1.0,
            status="ok",
            document_id="real_doc_id",
            counts={"document_id": "bogus_value_from_counts", "status": "bogus_status"},
        )

    message = records[0]
    assert "document_id=real_doc_id" in message
    assert "bogus_value_from_counts" not in message
    assert "status=ok" in message


def test_log_stage_result_omits_none_fields() -> None:
    logger = logging.getLogger("test.stage_logger.none_fields")
    records = []
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(logger, "log", lambda level, fmt, *args: records.append(fmt % args))
        log_stage_result(
            logger,
            stage_name="my_stage",
            duration_ms=1.0,
            status="ok",
        )

    message = records[0]
    assert "document_id" not in message
    assert "ingestion_run_id" not in message


def test_time_stage_logs_info_on_success_with_scope_counts(caplog) -> None:
    logger = logging.getLogger("test.stage_logger.time_stage_success")

    with caplog.at_level("INFO", logger=logger.name):
        with time_stage(logger, "widget_stage", document_id="doc_2") as scope:
            scope.counts["widgets_processed"] = 5

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.INFO
    message = record.getMessage()
    assert "stage=widget_stage" in message
    assert "status=ok" in message
    assert "widgets_processed=5" in message
    assert "document_id=doc_2" in message


def test_time_stage_success_level_can_be_downgraded_to_debug(caplog) -> None:
    logger = logging.getLogger("test.stage_logger.time_stage_debug")

    with caplog.at_level("DEBUG", logger=logger.name):
        with time_stage(logger, "detail_stage", success_level=logging.DEBUG):
            pass

    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.DEBUG


def test_time_stage_logs_error_and_reraises_on_exception(caplog) -> None:
    logger = logging.getLogger("test.stage_logger.time_stage_failure")

    with caplog.at_level("DEBUG", logger=logger.name):
        with pytest.raises(ValueError, match="boom"):
            with time_stage(logger, "failing_stage", document_id="doc_3") as scope:
                scope.counts["partial_progress"] = 1
                raise ValueError("boom")

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.ERROR
    message = record.getMessage()
    assert "stage=failing_stage" in message
    assert "status=failed" in message
    assert "error=boom" in message
    assert "partial_progress=1" in message


def test_time_stage_warn_if_emits_warning_without_changing_success_level(caplog) -> None:
    logger = logging.getLogger("test.stage_logger.time_stage_warn")

    with caplog.at_level("INFO", logger=logger.name):
        with time_stage(
            logger,
            "reconciled_stage",
            warn_if=lambda scope: (
                "conflict!" if scope.counts.get("conflict_count") else None
            ),
        ) as scope:
            scope.counts["conflict_count"] = 2

    assert len(caplog.records) == 2
    info_record, warning_record = caplog.records
    assert info_record.levelno == logging.INFO
    assert "status=ok" in info_record.getMessage()
    assert warning_record.levelno == logging.WARNING
    assert "conflict!" in warning_record.getMessage()


def test_time_stage_warn_if_stays_silent_when_no_warning_condition() -> None:
    logger = logging.getLogger("test.stage_logger.time_stage_no_warn")

    with pytest.MonkeyPatch.context() as mp:
        warnings_logged = []
        mp.setattr(logger, "warning", lambda *a, **kw: warnings_logged.append(a))
        with time_stage(logger, "clean_stage", warn_if=lambda scope: None):
            pass

    assert warnings_logged == []
