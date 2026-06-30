from io import StringIO
from time import sleep

import pytest

from src.application.agent_runtime.progress import ProgressIndicator


def test_progress_disabled_in_quiet_mode() -> None:
    stream = StringIO()
    indicator = ProgressIndicator(enabled=False, stream=stream, interval_seconds=0.01)

    result = indicator.run_with_progress(["Routing request"], lambda: "done")

    assert result == "done"
    assert stream.getvalue() == ""


def test_progress_disabled_for_json_output() -> None:
    stream = StringIO()
    indicator = ProgressIndicator(enabled=False, stream=stream, interval_seconds=0.01)

    indicator.run_with_progress(["Retrieving evidence"], lambda: "done")

    assert stream.getvalue() == ""


def test_progress_renders_stage_text_in_console_mode() -> None:
    stream = StringIO()
    indicator = ProgressIndicator(enabled=True, stream=stream, interval_seconds=0.01)

    indicator.run_with_progress(["Retrieving evidence"], lambda: sleep(0.03))

    assert "Retrieving evidence..." in stream.getvalue()


def test_progress_does_not_throw_on_windows_compatible_output() -> None:
    stream = StringIO()
    indicator = ProgressIndicator(enabled=True, stream=stream, interval_seconds=0.01)

    indicator.run_with_progress(["Generating grounded answer"], lambda: "done")

    assert "[ok]" in stream.getvalue()


def test_progress_handles_failures() -> None:
    stream = StringIO()
    indicator = ProgressIndicator(enabled=True, stream=stream, interval_seconds=0.01)

    with pytest.raises(RuntimeError):
        indicator.run_with_progress(
            ["Routing request"],
            lambda: (_ for _ in ()).throw(RuntimeError("boom")),
        )

    assert "[failed]" in stream.getvalue()
