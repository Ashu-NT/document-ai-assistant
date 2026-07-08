from __future__ import annotations

"""
Report tool: reads the application log and computes how often
RetrievalQueryIntentInferer falls back to RetrievalQueryIntent.GENERAL.

Relies on two log lines emitted by
`src/application/workflows/retrieval/retrieval_query_intent_inferer.py`:
  - "retrieval_intent_resolved intent=<value> query_id=<id>" - emitted on
    every call to `infer()`, regardless of outcome. This is the denominator.
  - "retrieval_intent_fallback_general reason=<reason> ..." - emitted only
    when the result is GENERAL, tagged with why (query_is_none,
    empty_query_text, no_pattern_matched). `no_pattern_matched` also carries
    the offending `query_text=...` so you can see what's slipping through
    the keyword/regex rules.

Usage:
    # Default: reads outputs/logs/application.log (from .env LOG_FILE)
    python scripts/report_retrieval_intent_fallback_rate.py

    # Point at a specific file, include rotated backups (.1, .2, ...)
    python scripts/report_retrieval_intent_fallback_rate.py --log-file outputs/logs/application.log --include-rotated

    # Print the actual query text of every no_pattern_matched fallback
    python scripts/report_retrieval_intent_fallback_rate.py --show-samples 20
"""

import argparse
import ast
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

_RESOLVED_PATTERN = re.compile(r"retrieval_intent_resolved intent=(?P<intent>\S+)")
_FALLBACK_PATTERN = re.compile(
    r"retrieval_intent_fallback_general reason=(?P<reason>\S+)"
)
_QUERY_TEXT_PATTERN = re.compile(r"query_text=(?P<query_text>'.*')\s*$")


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


def _extract_query_text(line: str) -> str | None:
    match = _QUERY_TEXT_PATTERN.search(line)
    if not match:
        return None
    try:
        return ast.literal_eval(match.group("query_text"))
    except (ValueError, SyntaxError):
        return match.group("query_text")


def analyze(lines: Sequence[str]) -> dict:
    intent_counts: Counter[str] = Counter()
    fallback_reason_counts: Counter[str] = Counter()
    no_pattern_matched_samples: list[str] = []

    for line in lines:
        resolved_match = _RESOLVED_PATTERN.search(line)
        if resolved_match:
            intent_counts[resolved_match.group("intent")] += 1
            continue

        fallback_match = _FALLBACK_PATTERN.search(line)
        if fallback_match:
            reason = fallback_match.group("reason")
            fallback_reason_counts[reason] += 1
            if reason == "no_pattern_matched":
                query_text = _extract_query_text(line)
                if query_text is not None:
                    no_pattern_matched_samples.append(query_text)

    total = sum(intent_counts.values())
    general = intent_counts.get("general", 0)
    return {
        "total": total,
        "general": general,
        "intent_counts": intent_counts,
        "fallback_reason_counts": fallback_reason_counts,
        "no_pattern_matched_samples": no_pattern_matched_samples,
    }


def _print_report(stats: dict, *, show_samples: int) -> None:
    total = stats["total"]
    general = stats["general"]

    if total == 0:
        print("No 'retrieval_intent_resolved' log lines found.")
        print(
            "Either the log file is empty/missing, or the app hasn't served "
            "any queries yet since this instrumentation was added."
        )
        return

    percentage = (general / total) * 100
    print(f"Total intent resolutions : {total}")
    print(f"Fell back to GENERAL     : {general} ({percentage:.1f}%)")
    print()

    print("By intent:")
    for intent, count in stats["intent_counts"].most_common():
        share = (count / total) * 100
        print(f"  {intent:<20} {count:>6}  ({share:5.1f}%)")
    print()

    if stats["fallback_reason_counts"]:
        print("GENERAL fallback reasons:")
        for reason, count in stats["fallback_reason_counts"].most_common():
            print(f"  {reason:<20} {count:>6}")
        print()

    samples = stats["no_pattern_matched_samples"]
    if samples and show_samples > 0:
        print(f"Sample queries with reason=no_pattern_matched (up to {show_samples}):")
        for query_text in samples[:show_samples]:
            print(f"  - {query_text}")


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
    parser.add_argument(
        "--show-samples",
        type=int,
        default=10,
        help="Number of raw no_pattern_matched query texts to print (0 to disable)",
    )
    args = parser.parse_args(argv)

    log_file = args.log_file or _default_log_path()
    files = _candidate_log_files(log_file, include_rotated=args.include_rotated)
    if not files:
        print(f"No log file(s) found at {log_file} (or its rotated backups).")
        return 1

    lines: list[str] = []
    for path in files:
        lines.extend(path.read_text(encoding="utf-8", errors="replace").splitlines())

    stats = analyze(lines)
    _print_report(stats, show_samples=args.show_samples)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
