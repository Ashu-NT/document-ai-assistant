from __future__ import annotations

from types import SimpleNamespace

from tests.unit.cli_scripts._test_cli_scripts_part1 import _load_script


def _mod():
    return _load_script("check_answer_quality_regression")


def _fake_report(*, average_score, case_count=1, judged_count=1):
    return SimpleNamespace(
        average_score=average_score,
        cases=[object()] * case_count,
        judged_cases=[object()] * judged_count,
    )


class _FakeJudgeRuntime:
    def __init__(self):
        self.answer_question_tool = object()
        self.judge_llm_service = object()
        self.judge_model = "qwen2.5:3b"


class _FakeJudgeModule:
    def __init__(self, *, report):
        self._report = report
        self.closed_runtime = None
        self.printed_report = None

    def build_judge_runtime(self, *, judge_model):
        return _FakeJudgeRuntime()

    def run_golden_set(self, cases, **kwargs):
        return self._report

    def print_report(self, report):
        self.printed_report = report

    def close_runtime(self, runtime):
        self.closed_runtime = runtime


# --- parse_args -------------------------------------------------------


def test_parse_args_defaults():
    mod = _mod()
    args = mod.parse_args([])
    assert args.threshold == mod._DEFAULT_THRESHOLD
    assert args.baseline == mod._DEFAULT_BASELINE_PATH
    assert args.update_baseline is False
    assert args.limit is None
    assert args.judge_model is None


def test_parse_args_overrides(tmp_path):
    mod = _mod()
    baseline_path = tmp_path / "baseline.json"
    args = mod.parse_args(
        [
            "--baseline",
            str(baseline_path),
            "--threshold",
            "0.1",
            "--update-baseline",
            "--limit",
            "3",
            "--judge-model",
            "qwen2.5:7b",
        ]
    )
    assert args.baseline == baseline_path
    assert args.threshold == 0.1
    assert args.update_baseline is True
    assert args.limit == 3
    assert args.judge_model == "qwen2.5:7b"


# --- load_baseline / write_baseline ------------------------------------


def test_load_baseline_returns_none_when_file_is_missing(tmp_path):
    mod = _mod()
    assert mod.load_baseline(tmp_path / "does_not_exist.json") is None


def test_write_baseline_then_load_baseline_round_trips(tmp_path):
    mod = _mod()
    path = tmp_path / "nested" / "baseline.json"
    mod.write_baseline(path, average_score=0.82, case_count=5, judged_count=5)

    baseline = mod.load_baseline(path)
    assert baseline.average_score == 0.82
    assert baseline.case_count == 5
    assert baseline.judged_count == 5


# --- evaluate_regression -------------------------------------------------


def test_evaluate_regression_fails_when_nothing_was_judged():
    mod = _mod()
    result = mod.evaluate_regression(
        current_average=None,
        baseline=mod.Baseline(average_score=0.8, case_count=5, judged_count=5),
        threshold=0.05,
    )
    assert result.regressed is True
    assert result.delta is None


def test_evaluate_regression_passes_with_no_prior_baseline():
    mod = _mod()
    result = mod.evaluate_regression(current_average=0.7, baseline=None, threshold=0.05)
    assert result.regressed is False
    assert result.delta is None
    assert "No baseline found" in result.message


def test_evaluate_regression_fails_beyond_threshold():
    mod = _mod()
    baseline = mod.Baseline(average_score=0.85, case_count=5, judged_count=5)
    result = mod.evaluate_regression(current_average=0.70, baseline=baseline, threshold=0.05)
    assert result.regressed is True
    assert round(result.delta, 6) == 0.15


def test_evaluate_regression_passes_within_threshold():
    mod = _mod()
    baseline = mod.Baseline(average_score=0.85, case_count=5, judged_count=5)
    result = mod.evaluate_regression(current_average=0.82, baseline=baseline, threshold=0.05)
    assert result.regressed is False


def test_evaluate_regression_passes_on_improvement():
    mod = _mod()
    baseline = mod.Baseline(average_score=0.70, case_count=5, judged_count=5)
    result = mod.evaluate_regression(current_average=0.90, baseline=baseline, threshold=0.05)
    assert result.regressed is False
    assert result.delta < 0


# --- main() orchestration -----------------------------------------------


def test_main_passes_and_reports_no_baseline_on_first_run(tmp_path, monkeypatch):
    mod = _mod()
    fake_module = _FakeJudgeModule(report=_fake_report(average_score=0.8))
    monkeypatch.setattr(mod, "_load_judge_module", lambda: fake_module)
    monkeypatch.setattr(
        mod, "load_golden_answer_cases", lambda: [object(), object()]
    )

    exit_code = mod.main(["--baseline", str(tmp_path / "baseline.json")])

    assert exit_code == 0
    assert fake_module.printed_report is not None
    assert fake_module.closed_runtime is not None


def test_main_fails_on_regression_beyond_threshold(tmp_path, monkeypatch):
    mod = _mod()
    baseline_path = tmp_path / "baseline.json"
    mod.write_baseline(baseline_path, average_score=0.9, case_count=3, judged_count=3)
    fake_module = _FakeJudgeModule(report=_fake_report(average_score=0.6))
    monkeypatch.setattr(mod, "_load_judge_module", lambda: fake_module)
    monkeypatch.setattr(mod, "load_golden_answer_cases", lambda: [object()])

    exit_code = mod.main(["--baseline", str(baseline_path)])

    assert exit_code == 1


def test_main_passes_when_within_threshold(tmp_path, monkeypatch):
    mod = _mod()
    baseline_path = tmp_path / "baseline.json"
    mod.write_baseline(baseline_path, average_score=0.9, case_count=3, judged_count=3)
    fake_module = _FakeJudgeModule(report=_fake_report(average_score=0.87))
    monkeypatch.setattr(mod, "_load_judge_module", lambda: fake_module)
    monkeypatch.setattr(mod, "load_golden_answer_cases", lambda: [object()])

    exit_code = mod.main(["--baseline", str(baseline_path)])

    assert exit_code == 0


def test_main_fails_when_nothing_was_judged(tmp_path, monkeypatch):
    mod = _mod()
    fake_module = _FakeJudgeModule(report=_fake_report(average_score=None, judged_count=0))
    monkeypatch.setattr(mod, "_load_judge_module", lambda: fake_module)
    monkeypatch.setattr(mod, "load_golden_answer_cases", lambda: [object()])

    exit_code = mod.main(["--baseline", str(tmp_path / "baseline.json")])

    assert exit_code == 1


def test_main_writes_updated_baseline_when_requested(tmp_path, monkeypatch):
    mod = _mod()
    baseline_path = tmp_path / "baseline.json"
    fake_module = _FakeJudgeModule(report=_fake_report(average_score=0.77, case_count=4, judged_count=4))
    monkeypatch.setattr(mod, "_load_judge_module", lambda: fake_module)
    monkeypatch.setattr(mod, "load_golden_answer_cases", lambda: [object()] * 4)

    exit_code = mod.main(["--baseline", str(baseline_path), "--update-baseline"])

    assert exit_code == 0
    written = mod.load_baseline(baseline_path)
    assert written.average_score == 0.77
    assert written.case_count == 4
    assert written.judged_count == 4


def test_main_respects_limit_by_slicing_cases(tmp_path, monkeypatch):
    mod = _mod()
    fake_module = _FakeJudgeModule(report=_fake_report(average_score=0.8))
    received_cases = {}

    def _fake_run_golden_set(cases, **kwargs):
        received_cases["cases"] = cases
        return fake_module._report

    fake_module.run_golden_set = _fake_run_golden_set
    monkeypatch.setattr(mod, "_load_judge_module", lambda: fake_module)
    monkeypatch.setattr(
        mod, "load_golden_answer_cases", lambda: [object(), object(), object()]
    )

    mod.main(["--baseline", str(tmp_path / "baseline.json"), "--limit", "1"])

    assert len(received_cases["cases"]) == 1
