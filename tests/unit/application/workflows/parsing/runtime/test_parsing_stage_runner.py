import logging

import pytest

from src.application.workflows.parsing.runtime.parsing_stage_runner import run_stage

_LOGGER_NAME = "src.application.workflows.parsing.runtime.parsing_stage_runner"


def test_run_stage_logs_completion_and_records_duration(caplog) -> None:
    stage_durations: dict[str, float] = {}

    with caplog.at_level("INFO", logger=_LOGGER_NAME):
        result = run_stage(
            progress_callback=None,
            start_message="starting",
            heartbeat_label="widget stage",
            failure_label="widget stage",
            operation=lambda: "done",
            completion_message_builder=lambda _r, _e: "finished",
            stage_name="widget_stage",
            stage_durations=stage_durations,
            document_id="doc_1",
        )

    assert result == "done"
    assert "widget_stage" in stage_durations
    assert len(caplog.records) == 1
    message = caplog.records[0].getMessage()
    assert "stage=widget_stage" in message
    assert "status=ok" in message
    assert "document_id=doc_1" in message


def test_run_stage_logs_error_and_reraises_on_failure(caplog) -> None:
    def _boom():
        raise RuntimeError("stage exploded")

    with caplog.at_level("DEBUG", logger=_LOGGER_NAME):
        with pytest.raises(RuntimeError, match="stage exploded"):
            run_stage(
                progress_callback=None,
                start_message="starting",
                heartbeat_label="widget stage",
                failure_label="widget stage",
                operation=_boom,
                completion_message_builder=lambda _r, _e: "finished",
                stage_name="widget_stage",
                document_id="doc_2",
            )

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.ERROR
    message = record.getMessage()
    assert "stage=widget_stage" in message
    assert "status=failed" in message
    assert "error=stage exploded" in message
    assert "document_id=doc_2" in message


def test_run_stage_falls_back_to_heartbeat_label_when_stage_name_omitted(caplog) -> None:
    with caplog.at_level("INFO", logger=_LOGGER_NAME):
        run_stage(
            progress_callback=None,
            start_message="starting",
            heartbeat_label="unnamed stage",
            failure_label="unnamed stage",
            operation=lambda: None,
            completion_message_builder=lambda _r, _e: "finished",
        )

    assert "stage=unnamed stage" in caplog.records[0].getMessage()
