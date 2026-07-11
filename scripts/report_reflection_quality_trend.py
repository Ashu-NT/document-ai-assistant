from __future__ import annotations

"""
Report tool: reads the application log and aggregates reflection's per-turn
quality scores and decisions.

Relies on a structured log line emitted by
`src/application/langgraph/reflection/services/reflection_service.py`:
  - `logger.info("reflection_score_recorded", extra={"decision": ...,
    "answer_quality_score": ..., "evidence_quality_score": ...,
    "grounding_score": ..., "overall_score": ...})`

This mirrors the exact pattern already established by
`scripts/report_retrieval_intent_fallback_rate.py`, which parses a similar
structured log line emitted by `retrieval_query_intent_inferer.py` into an
aggregate fallback rate.

IMPORTANT CAVEAT (see the module docstring of the sibling script's report
for the analogous log-file-path caveat -- this one is about the log-line
*content*, not its location): the reflection log call above passes its
fields only via the stdlib logging `extra={...}` kwarg. This repo's global
logging format string (`src/config/logging/logging_config.py`) is
`"%(asctime)s | %(levelname)s | %(name)s | %(message)s"`, which does **not**
interpolate `extra` fields into the rendered line -- only the literal
message `"reflection_score_recorded"` ends up in the text. By contrast,
`retrieval_query_intent_inferer.py` (the sibling script's data source)
embeds its fields directly in the message string via `%s` placeholders,
which is why that report can actually recover values from the log text.
Verified empirically: logging with this exact call/formatter combination
renders as `"... | reflection_score_recorded"` with no score/decision
fields anywhere in the line.

Rather than silently reporting zeroes, this script still counts real
`reflection_score_recorded` events (that part works today), and clearly
flags when scores/decision could not be recovered from the log text, so the
gap is visible instead of being mistaken for "reflection never runs."
Should the logging call (or the global formatter) later be changed to also
embed these fields as `key=value` text -- e.g.
`"reflection_score_recorded decision=%s answer_quality_score=%s ..."`,
matching the sibling convention -- this script's regexes already parse that
shape with no changes required.

Usage:
    # Default: reads outputs/logs/application.log (from .env LOG_FILE)
    python scripts/report_reflection_quality_trend.py

    # Point at a specific file, include rotated backups (.1, .2, ...)
    python scripts/report_reflection_quality_trend.py --log-file outputs/logs/application.log --include-rotated
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

_EVENT_MARKER = "reflection_score_recorded"
_DECISION_PATTERN = re.compile(r"decision=(?P<decision>\S+)")
_ANSWER_QUALITY_PATTERN = re.compile(
    r"answer_quality_score=(?P<value>-?\d+(?:\.\d+)?)"
)
_EVIDENCE_QUALITY_PATTERN = re.compile(
    r"evidence_quality_score=(?P<value>-?\d+(?:\.\d+)?)"
)
_GROUNDING_PATTERN = re.compile(r"grounding_score=(?P<value>-?\d+(?:\.\d+)?)")
_OVERALL_PATTERN = re.compile(r"overall_score=(?P<value>-?\d+(?:\.\d+)?)")

_SCORE_FIELDS: tuple[tuple[str, re.Pattern], ...] = (
    ("answer_quality_score", _ANSWER_QUALITY_PATTERN),
    ("evidence_quality_score", _EVIDENCE_QUALITY_PATTERN),
    ("grounding_score", _GROUNDING_PATTERN),
    ("overall_score", _OVERALL_PATTERN),
)


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
    total_events = 0
    parsed_events = 0
    decision_counts: Counter[str] = Counter()
    score_sums: dict[str, float] = {name: 0.0 for name, _ in _SCORE_FIELDS}
    score_counts: dict[str, int] = {name: 0 for name, _ in _SCORE_FIELDS}

    for line in lines:
        if _EVENT_MARKER not in line:
            continue
        total_events += 1

        decision_match = _DECISION_PATTERN.search(line)
        if decision_match:
            decision_counts[decision_match.group("decision")] += 1

        line_scores_found = 0
        for field_name, pattern in _SCORE_FIELDS:
            match = pattern.search(line)
            if match:
                score_sums[field_name] += float(match.group("value"))
                score_counts[field_name] += 1
                line_scores_found += 1

        if decision_match and line_scores_found == len(_SCORE_FIELDS):
            parsed_events += 1

    average_scores = {
        name: (score_sums[name] / score_counts[name] if score_counts[name] else None)
        for name, _ in _SCORE_FIELDS
    }

    return {
        "total_events": total_events,
        "parsed_events": parsed_events,
        "unparsed_events": total_events - parsed_events,
        "decision_counts": decision_counts,
        "average_scores": average_scores,
        "score_counts": score_counts,
    }


def _print_report(stats: dict) -> None:
    total_events = stats["total_events"]

    if total_events == 0:
        print("No 'reflection_score_recorded' log lines found.")
        print(
            "Either the log file is empty/missing, reflection is disabled "
            "(reflection_enabled defaults to False), or the app hasn't "
            "answered any questions with reflection turned on yet."
        )
        return

    print(f"Total reflection events   : {total_events}")
    print(f"Events with parsable scores: {stats['parsed_events']}")
    print()

    print("Average scores (over events where the field was recoverable):")
    for field_name, average in stats["average_scores"].items():
        count = stats["score_counts"][field_name]
        if average is None:
            print(f"  {field_name:<24} n/a (0 values found)")
        else:
            print(f"  {field_name:<24} {average:.4f}  (n={count})")
    print()

    if stats["decision_counts"]:
        print("Decision breakdown:")
        for decision, count in stats["decision_counts"].most_common():
            share = (count / total_events) * 100
            print(f"  {decision:<24} {count:>6}  ({share:5.1f}%)")
    else:
        print("Decision breakdown: no 'decision=' values found in any event line.")

    if stats["unparsed_events"] > 0:
        print()
        print(
            f"NOTE: {stats['unparsed_events']} of {total_events} "
            "'reflection_score_recorded' event(s) did not have all 4 scores "
            "+ decision recoverable as key=value text on the same line. This "
            "is expected today: the current logging call passes its fields "
            "only via logging's `extra={...}` kwarg, and this repo's global "
            "log format string does not interpolate `extra` fields into the "
            "rendered message -- see this script's module docstring."
        )


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
        return 1

    lines: list[str] = []
    for path in files:
        lines.extend(path.read_text(encoding="utf-8", errors="replace").splitlines())

    stats = analyze(lines)
    _print_report(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
