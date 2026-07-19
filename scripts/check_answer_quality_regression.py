from __future__ import annotations

"""
Local pre-merge gate for answer-quality regressions (W10,
outputs/architecture/answering_flow_weakness_remediation_plan.md).

Runs the golden answer set through the exact same measurement path as
`scripts/run_answer_quality_judge.py` (real pipeline generation + independent
LLM-as-judge scoring -- reused here via dynamic module load, not duplicated),
then compares the resulting average score against a stored baseline and
exits non-zero if it dropped by more than `--threshold`.

This is this repo's de facto CI for answer quality the same way
`scripts/check_source_mojibake.py` (paired with
`tests/unit/test_no_source_mojibake.py`) is de facto CI for mojibake: run it
locally before merging a change that could plausibly affect generated
answers. Unlike the mojibake check, this one needs a live Ollama instance
and a real LLM-as-judge pass, so it is deliberately NOT wired into
`pytest tests/unit/` -- it stays a standalone, manually-invoked gate.

Usage:
    # First run: establish a baseline (no prior baseline to regress against)
    python scripts/check_answer_quality_regression.py --update-baseline

    # Normal use: compare against the stored baseline, fail on regression
    python scripts/check_answer_quality_regression.py

    # After a deliberate, reviewed quality improvement/change in expectations
    python scripts/check_answer_quality_regression.py --update-baseline

    python scripts/check_answer_quality_regression.py --threshold 0.1 --limit 5
"""

import argparse
import importlib.util
import json
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for _import_root in (PROJECT_ROOT, SRC_ROOT):
    _import_root_str = str(_import_root)
    if _import_root_str not in sys.path:
        sys.path.insert(0, _import_root_str)

from src.application.evaluation.answer_quality import load_golden_answer_cases  # noqa: E402

_DEFAULT_BASELINE_PATH = (
    PROJECT_ROOT / "outputs" / "evaluation" / "answer_quality" / "baseline_score.json"
)
_DEFAULT_THRESHOLD = 0.05


@dataclass(slots=True)
class Baseline:
    average_score: float
    case_count: int
    judged_count: int


@dataclass(slots=True)
class RegressionResult:
    regressed: bool
    delta: float | None
    message: str


def _load_judge_module():
    """Dynamically loads scripts/run_answer_quality_judge.py so its existing
    golden-set/judge-runtime/scoring machinery can be reused here instead of
    duplicating it -- the same load-by-path technique that script itself
    already uses for scripts/ask_document.py (`_load_ask_document_module()`),
    which in turn mirrors the test-side `_load_script()` helper in
    tests/unit/cli_scripts/_test_cli_scripts_part1.py."""
    cache_key = "_check_answer_quality_regression_judge_module"
    if cache_key in sys.modules:
        return sys.modules[cache_key]

    script_path = PROJECT_ROOT / "scripts" / "run_answer_quality_judge.py"
    saved_path = list(sys.path)
    spec = importlib.util.spec_from_file_location(cache_key, script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[cache_key] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(cache_key, None)
        raise
    finally:
        sys.path[:] = saved_path
    return module


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        type=Path,
        default=_DEFAULT_BASELINE_PATH,
        metavar="PATH",
        help=f"Path to the stored baseline JSON (default: {_DEFAULT_BASELINE_PATH}).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=_DEFAULT_THRESHOLD,
        metavar="SCORE",
        help=(
            "Maximum allowed drop in average score, on the 0.0-1.0 scale, "
            f"before this is treated as a regression (default: {_DEFAULT_THRESHOLD})."
        ),
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="After measuring, write the current average score as the new baseline.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Only run the first N golden cases (default: all).",
    )
    parser.add_argument(
        "--judge-model",
        default=None,
        metavar="MODEL",
        help="Override the LLM model used for the judge pass (defaults to GENERAL_LLM).",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str) -> None:
    print(f"[answer-quality-regression] {message}", flush=True)


def load_baseline(path: Path) -> Baseline | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return Baseline(
        average_score=float(payload["average_score"]),
        case_count=int(payload.get("case_count", 0)),
        judged_count=int(payload.get("judged_count", 0)),
    )


def write_baseline(
    path: Path, *, average_score: float, case_count: int, judged_count: int
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "average_score": average_score,
                "case_count": case_count,
                "judged_count": judged_count,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def evaluate_regression(
    *,
    current_average: float | None,
    baseline: Baseline | None,
    threshold: float,
) -> RegressionResult:
    """Pure decision logic, isolated from measurement the same way
    `judge_answer()`/`_parse_judge_response()` in run_answer_quality_judge.py
    isolate LLM-judging from orchestration -- fully unit-testable with no
    LLM or pipeline dependency.

    `current_average is None` (nothing was successfully judged this run,
    e.g. Ollama unreachable) is deliberately treated as a failure, not a
    pass: silently reporting "no regression" when quality couldn't actually
    be measured would defeat the entire point of this gate (W10's own
    "Why it matters": regressions surfacing only via indefinite manual
    spot-check)."""
    if current_average is None:
        return RegressionResult(
            regressed=True,
            delta=None,
            message=(
                "No cases were successfully judged this run (see skipped-case "
                "detail above) -- cannot confirm no regression, so this counts "
                "as a failure."
            ),
        )
    if baseline is None:
        return RegressionResult(
            regressed=False,
            delta=None,
            message=(
                f"No baseline found; current average score is {current_average:.3f}. "
                "Re-run with --update-baseline to record it as the baseline."
            ),
        )
    delta = baseline.average_score - current_average
    if delta > threshold:
        return RegressionResult(
            regressed=True,
            delta=delta,
            message=(
                f"Regression: average score dropped from {baseline.average_score:.3f} "
                f"(baseline) to {current_average:.3f} (delta -{delta:.3f}, "
                f"threshold {threshold:.3f})."
            ),
        )
    return RegressionResult(
        regressed=False,
        delta=delta,
        message=(
            f"No regression: average score {current_average:.3f} vs. baseline "
            f"{baseline.average_score:.3f} (delta {-delta:+.3f}, threshold {threshold:.3f})."
        ),
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    judge_module = _load_judge_module()
    runtime = None

    try:
        cases = load_golden_answer_cases()
        if args.limit is not None:
            cases = cases[: args.limit]
        print_status(f"Loaded {len(cases)} golden answer case(s).")

        baseline = load_baseline(args.baseline)
        if baseline is not None:
            print_status(f"Baseline: {baseline.average_score:.3f} ({args.baseline}).")
        else:
            print_status(f"No baseline file found at {args.baseline}.")

        print_status("Building answer-quality judge runtime...")
        runtime = judge_module.build_judge_runtime(judge_model=args.judge_model)
        print_status(f"Judge model: {runtime.judge_model or '(default)'}")

        report = judge_module.run_golden_set(
            cases,
            answer_question_tool=runtime.answer_question_tool,
            judge_llm_service=runtime.judge_llm_service,
            judge_model=runtime.judge_model,
            progress_callback=print_status,
        )
        judge_module.print_report(report)

        result = evaluate_regression(
            current_average=report.average_score,
            baseline=baseline,
            threshold=args.threshold,
        )
        print()
        print_status(result.message)

        if args.update_baseline and report.average_score is not None:
            write_baseline(
                args.baseline,
                average_score=report.average_score,
                case_count=len(report.cases),
                judged_count=len(report.judged_cases),
            )
            print_status(f"Wrote updated baseline to {args.baseline}.")

        return 1 if result.regressed else 0
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    finally:
        if runtime is not None:
            judge_module.close_runtime(runtime)


if __name__ == "__main__":
    raise SystemExit(main())
