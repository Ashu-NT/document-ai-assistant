from __future__ import annotations

from tests.unit.cli_scripts._test_cli_scripts_part1 import _load_script


def _mod():
    return _load_script("report_reflection_quality_trend")


def _event_line(
    *,
    decision: str = "ACCEPT",
    answer_quality_score: float = 0.8,
    evidence_quality_score: float = 0.7,
    grounding_score: float = 0.7,
    overall_score: float = 0.75,
) -> str:
    """A synthetic log line in the shape this script's regexes are designed
    to parse -- key=value tokens on the same line as the event marker, the
    same convention `retrieval_intent_resolved`/`retrieval_intent_fallback_general`
    already use in `retrieval_query_intent_inferer.py`. This does NOT
    reflect what `reflection_service.py`'s current `extra={...}`-only log
    call actually renders as (see the script's module docstring) -- it
    exercises the parsing logic against the shape it is built to handle."""
    return (
        "2026-07-12 10:00:00,000 | INFO | "
        "src.application.langgraph.reflection.services.reflection_service | "
        "reflection_score_recorded decision="
        f"{decision} answer_quality_score={answer_quality_score} "
        f"evidence_quality_score={evidence_quality_score} "
        f"grounding_score={grounding_score} overall_score={overall_score}"
    )


# --- analyze() -------------------------------------------------------------


def test_analyze_returns_zero_totals_on_empty_input():
    mod = _mod()
    stats = mod.analyze([])
    assert stats["total_events"] == 0
    assert stats["parsed_events"] == 0
    assert stats["decision_counts"] == {}
    assert all(value is None for value in stats["average_scores"].values())


def test_analyze_ignores_unrelated_lines():
    mod = _mod()
    stats = mod.analyze(
        [
            "2026-07-12 10:00:00,000 | INFO | some.module | unrelated_event foo=bar",
            "2026-07-12 10:00:01,000 | INFO | some.module | retrieval_intent_resolved intent=general",
        ]
    )
    assert stats["total_events"] == 0


def test_analyze_counts_events_and_computes_averages():
    mod = _mod()
    lines = [
        _event_line(
            decision="ACCEPT",
            answer_quality_score=1.0,
            evidence_quality_score=1.0,
            grounding_score=1.0,
            overall_score=1.0,
        ),
        _event_line(
            decision="ACCEPT_WITH_LIMITATIONS",
            answer_quality_score=0.5,
            evidence_quality_score=0.5,
            grounding_score=0.5,
            overall_score=0.5,
        ),
    ]
    stats = mod.analyze(lines)

    assert stats["total_events"] == 2
    assert stats["parsed_events"] == 2
    assert stats["unparsed_events"] == 0
    assert stats["average_scores"]["answer_quality_score"] == 0.75
    assert stats["average_scores"]["evidence_quality_score"] == 0.75
    assert stats["average_scores"]["grounding_score"] == 0.75
    assert stats["average_scores"]["overall_score"] == 0.75


def test_analyze_decision_breakdown_counts_each_decision():
    mod = _mod()
    lines = [
        _event_line(decision="ACCEPT"),
        _event_line(decision="ACCEPT"),
        _event_line(decision="RETRIEVE_AGAIN"),
        _event_line(decision="CLARIFY"),
        _event_line(decision="FAIL"),
    ]
    stats = mod.analyze(lines)

    assert stats["decision_counts"]["ACCEPT"] == 2
    assert stats["decision_counts"]["RETRIEVE_AGAIN"] == 1
    assert stats["decision_counts"]["CLARIFY"] == 1
    assert stats["decision_counts"]["FAIL"] == 1
    assert stats["total_events"] == 5


def test_analyze_marks_event_unparsed_when_scores_are_not_recoverable():
    """Mirrors what `reflection_service.py`'s real `extra={...}`-only log
    call actually renders as today: the event marker is present in the
    text but none of the score/decision fields are."""
    mod = _mod()
    lines = [
        "2026-07-12 10:00:00,000 | INFO | "
        "src.application.langgraph.reflection.services.reflection_service | "
        "reflection_score_recorded"
    ]
    stats = mod.analyze(lines)

    assert stats["total_events"] == 1
    assert stats["parsed_events"] == 0
    assert stats["unparsed_events"] == 1
    assert stats["decision_counts"] == {}
    assert all(value is None for value in stats["average_scores"].values())


def test_analyze_partial_line_with_some_fields_missing_is_unparsed():
    mod = _mod()
    lines = [
        "2026-07-12 10:00:00,000 | INFO | reflection | "
        "reflection_score_recorded decision=ACCEPT answer_quality_score=0.9"
    ]
    stats = mod.analyze(lines)

    assert stats["total_events"] == 1
    assert stats["parsed_events"] == 0
    assert stats["unparsed_events"] == 1
    assert stats["decision_counts"]["ACCEPT"] == 1
    assert stats["average_scores"]["answer_quality_score"] == 0.9
    assert stats["average_scores"]["evidence_quality_score"] is None


# --- _candidate_log_files() --------------------------------------------


def test_candidate_log_files_returns_empty_when_missing(tmp_path):
    mod = _mod()
    missing = tmp_path / "does_not_exist.log"
    files = mod._candidate_log_files(missing, include_rotated=False)
    assert files == []


def test_candidate_log_files_returns_existing_file(tmp_path):
    mod = _mod()
    log_file = tmp_path / "application.log"
    log_file.write_text("hello\n", encoding="utf-8")
    files = mod._candidate_log_files(log_file, include_rotated=False)
    assert files == [log_file]


def test_candidate_log_files_includes_rotated_backups(tmp_path):
    mod = _mod()
    log_file = tmp_path / "application.log"
    log_file.write_text("current\n", encoding="utf-8")
    rotated = tmp_path / "application.log.1"
    rotated.write_text("old\n", encoding="utf-8")

    files = mod._candidate_log_files(log_file, include_rotated=True)
    assert log_file in files
    assert rotated in files


# --- main() / argparse -----------------------------------------------


def test_main_reports_error_when_no_log_file_found(tmp_path, capsys):
    mod = _mod()
    missing = tmp_path / "nope.log"
    exit_code = mod.main(["--log-file", str(missing)])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "No log file(s) found" in captured.out


def test_main_reports_zero_events_for_empty_log(tmp_path, capsys):
    mod = _mod()
    log_file = tmp_path / "application.log"
    log_file.write_text("unrelated line\n", encoding="utf-8")

    exit_code = mod.main(["--log-file", str(log_file)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "No 'reflection_score_recorded' log lines found." in captured.out


def test_main_reports_parsed_events_for_populated_log(tmp_path, capsys):
    mod = _mod()
    log_file = tmp_path / "application.log"
    log_file.write_text(_event_line() + "\n", encoding="utf-8")

    exit_code = mod.main(["--log-file", str(log_file)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Total reflection events   : 1" in captured.out
    assert "ACCEPT" in captured.out
