from __future__ import annotations

from tests.unit.cli_scripts._test_cli_scripts_part1 import _load_script


def _mod():
    return _load_script("report_answer_intent_margin_distribution")


def _event_line(
    *,
    intent: str = "procedure_steps",
    confidence: float = 0.8,
    margin: int | None = 0,
    runner_up_intent: str | None = "troubleshooting",
) -> str:
    return (
        "2026-07-19 10:00:00,000 | INFO | "
        "src.application.services.answer_generation.intent.answer_intent_analyzer | "
        f"answer_intent_resolved intent={intent} confidence={confidence} "
        f"margin={margin if margin is not None else 'None'} "
        f"runner_up_intent={runner_up_intent if runner_up_intent is not None else 'None'} "
        "rules_version=v1"
    )


# --- analyze() -------------------------------------------------------------


def test_analyze_returns_zero_totals_on_empty_input():
    mod = _mod()
    stats = mod.analyze([])
    assert stats["total"] == 0
    assert stats["no_runner_up"] == 0
    assert stats["margin_counts"] == {}


def test_analyze_ignores_unrelated_lines():
    mod = _mod()
    stats = mod.analyze(
        [
            "2026-07-19 10:00:00,000 | INFO | some.module | unrelated_event foo=bar",
        ]
    )
    assert stats["total"] == 0


def test_analyze_counts_no_runner_up_separately_from_margins():
    mod = _mod()
    lines = [
        _event_line(margin=None, runner_up_intent=None),
        _event_line(margin=0, runner_up_intent="troubleshooting"),
    ]
    stats = mod.analyze(lines)

    assert stats["total"] == 2
    assert stats["no_runner_up"] == 1
    assert stats["margin_counts"] == {0: 1}


def test_analyze_builds_a_margin_histogram():
    mod = _mod()
    lines = [
        _event_line(margin=0),
        _event_line(margin=0),
        _event_line(margin=1),
        _event_line(margin=3),
    ]
    stats = mod.analyze(lines)

    assert stats["total"] == 4
    assert stats["margin_counts"] == {0: 2, 1: 1, 3: 1}


def test_analyze_caps_large_margins_at_the_histogram_cap():
    mod = _mod()
    lines = [_event_line(margin=50)]
    stats = mod.analyze(lines)

    assert stats["margin_counts"] == {mod._HISTOGRAM_CAP: 1}


def test_analyze_counts_intents():
    mod = _mod()
    lines = [
        _event_line(intent="procedure_steps"),
        _event_line(intent="procedure_steps"),
        _event_line(intent="table_summary"),
    ]
    stats = mod.analyze(lines)

    assert stats["intent_counts"]["procedure_steps"] == 2
    assert stats["intent_counts"]["table_summary"] == 1


# --- main() / argparse -----------------------------------------------


def test_main_reports_error_when_no_log_file_found(tmp_path, capsys):
    mod = _mod()
    missing = tmp_path / "nope.log"
    exit_code = mod.main(["--log-file", str(missing)])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "No log file(s) found" in captured.out


def test_main_reports_no_telemetry_for_empty_log(tmp_path, capsys):
    mod = _mod()
    log_file = tmp_path / "application.log"
    log_file.write_text("unrelated line\n", encoding="utf-8")

    exit_code = mod.main(["--log-file", str(log_file)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "No 'answer_intent_resolved' log lines found." in captured.out
    assert "explicitly deferred" in captured.out


def test_main_reports_margin_distribution_for_populated_log(tmp_path, capsys):
    mod = _mod()
    log_file = tmp_path / "application.log"
    log_file.write_text(
        _event_line(margin=0) + "\n" + _event_line(margin=1) + "\n",
        encoding="utf-8",
    )

    exit_code = mod.main(["--log-file", str(log_file)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Total intent resolutions : 2" in captured.out
    assert "margin=0" in captured.out
    assert "currently gated as contested" in captured.out
