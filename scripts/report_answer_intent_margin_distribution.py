from __future__ import annotations

"""
Report tool: reads the application log and computes the distribution of
AnswerIntentAnalyzer's winner/runner-up scoring margins -- the prerequisite
data W1 (answering_flow_weakness_remediation_plan.md) needs before ever
widening `AnswerIntentDecision.is_contested`'s threshold past an exact tie
(`margin == 0`). This is explicitly a data-driven decision, not a guess: run
this script and see where real near-misses cluster before touching the
threshold.

Relies on one log line emitted by
`src/application/services/answer_generation/intent/answer_intent_analyzer.py`:
  - "answer_intent_resolved intent=<value> confidence=<value>
    margin=<value|None> runner_up_intent=<value|None>
    rules_version=<value>" -- emitted on every call to `analyze()`.

Usage:
    # Default: reads outputs/logs/application.log (from .env LOG_FILE)
    python scripts/report_answer_intent_margin_distribution.py

    # Point at a specific file, include rotated backups (.1, .2, ...)
    python scripts/report_answer_intent_margin_distribution.py --log-file outputs/logs/application.log --include-rotated
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]

for _import_root in (PROJECT_ROOT,):
    _import_root_str = str(_import_root)
    if _import_root_str not in sys.path:
        sys.path.insert(0, _import_root_str)

_EVENT_MARKER = "answer_intent_resolved"
_MARGIN_PATTERN = re.compile(r"margin=(?P<margin>-?\d+|None)")
_INTENT_PATTERN = re.compile(r"answer_intent_resolved intent=(?P<intent>\S+)")

# Beyond this margin, a near-miss is unlikely to be a genuinely close call --
# grouped together in the report rather than diluting the histogram with a
# long tail of confidently-resolved margins.
_HISTOGRAM_CAP = 5


def _default_log_path() -> Path:
    try:
        from src.config.settings import logging_settings

        return Path(logging_settings.log_file)
    except Exception:
        return Path("outputs/logs/application.log")


def _candidate_log_files(log_file: Path, *, include_rotated: bool) -> list[Path]:
    files = [log_file] if log_file.exists() else []
    if include_rotated:
        parent = log_file.parent
        pattern = f"{log_file.name}.*"
        rotated = sorted(
            (path for path in parent.glob(pattern) if path.is_file()),
            key=lambda path: path.suffix,
        )
        files.extend(rotated)
    return files


def analyze(lines: Sequence[str]) -> dict:
    total = 0
    no_runner_up = 0
    margin_counts: Counter[int] = Counter()
    intent_counts: Counter[str] = Counter()

    for line in lines:
        if _EVENT_MARKER not in line:
            continue
        intent_match = _INTENT_PATTERN.search(line)
        margin_match = _MARGIN_PATTERN.search(line)
        if margin_match is None:
            continue
        total += 1
        if intent_match:
            intent_counts[intent_match.group("intent")] += 1
        raw_margin = margin_match.group("margin")
        if raw_margin == "None":
            no_runner_up += 1
            continue
        margin = min(int(raw_margin), _HISTOGRAM_CAP)
        margin_counts[margin] += 1

    return {
        "total": total,
        "no_runner_up": no_runner_up,
        "margin_counts": margin_counts,
        "intent_counts": intent_counts,
    }


def _print_report(stats: dict) -> None:
    total = stats["total"]

    if total == 0:
        print("No 'answer_intent_resolved' log lines found.")
        print(
            "No telemetry has been collected yet -- this is expected before "
            "the app has served any real questions. Widening "
            "AnswerIntentDecision.is_contested's threshold past an exact "
            "tie remains explicitly deferred until this report has real "
            "data to show where near-misses cluster (W1, "
            "answering_flow_weakness_remediation_plan.md)."
        )
        return

    print(f"Total intent resolutions : {total}")
    print(f"No runner-up at all      : {stats['no_runner_up']}")
    print()

    margin_counts = stats["margin_counts"]
    with_runner_up = sum(margin_counts.values())
    print("Margin distribution (winner score - runner-up score, among cases with a runner-up):")
    for margin in sorted(margin_counts):
        count = margin_counts[margin]
        share = (count / with_runner_up) * 100 if with_runner_up else 0.0
        label = f"{margin}" if margin < _HISTOGRAM_CAP else f"{_HISTOGRAM_CAP}+"
        marker = "  <- currently gated as contested" if margin == 0 else ""
        print(f"  margin={label:<4} {count:>6}  ({share:5.1f}%){marker}")
    print()

    if stats["intent_counts"]:
        print("By resolved intent:")
        for intent, count in stats["intent_counts"].most_common():
            share = (count / total) * 100
            print(f"  {intent:<24} {count:>6}  ({share:5.1f}%)")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Path to the application log file (defaults to LOG_FILE from .env)",
    )
    parser.add_argument(
        "--include-rotated",
        action="store_true",
        help="Also read rotated backups next to the log file (e.g. application.log.1)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    log_file = args.log_file or _default_log_path()
    files = _candidate_log_files(log_file, include_rotated=args.include_rotated)
    if not files:
        print(f"No log file(s) found at {log_file} (or its rotated backups).")
        _print_report({"total": 0, "no_runner_up": 0, "margin_counts": Counter(), "intent_counts": Counter()})
        return 1

    lines: list[str] = []
    for path in files:
        lines.extend(path.read_text(encoding="utf-8", errors="replace").splitlines())

    stats = analyze(lines)
    _print_report(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
