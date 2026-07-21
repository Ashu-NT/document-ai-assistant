from __future__ import annotations

"""
Replay tool: feeds a set of query texts through
`RetrievalQueryIntentInferer.infer()` and captures the resulting
"retrieval_intent_resolved"/"retrieval_intent_fallback_general" log lines
into a plain-text log file, in the exact format
`scripts/report_retrieval_intent_fallback_rate.py` expects.

Exists to exercise that report script end-to-end (and produce a first real
fallback-rate baseline) without needing a live application run. Prefers the
real benchmark truth-set corpus (gitignored, customer documents) when
present locally; falls back to a small built-in synthetic query set spanning
every intent plus known GENERAL-fallback cases (typo'd markers, one-word
queries, non-English text) when it isn't -- e.g. on a fresh checkout or CI.

Usage:
    python scripts/replay_retrieval_intent_log.py
    python scripts/replay_retrieval_intent_log.py --output outputs/logs/retrieval_intent_replay.log
    python scripts/report_retrieval_intent_fallback_rate.py --log-file outputs/logs/retrieval_intent_replay.log
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
for _import_root in (PROJECT_ROOT,):
    _import_root_str = str(_import_root)
    if _import_root_str not in sys.path:
        sys.path.insert(0, _import_root_str)

DEFAULT_OUTPUT_PATH = Path("outputs/logs/retrieval_intent_replay.log")

# Spans every RetrievalQueryIntent plus the known-fallback characterization
# cases documented in test_retrieval_query_intent_coverage_gaps.py, so a
# replay against this set alone already exercises both the "resolved" and
# the "fallback_general" log lines the report script parses.
_SYNTHETIC_QUERY_SET: tuple[str, ...] = (
    "What are the likely causes of pump vibration?",
    "How do I troubleshoot the pump?",
    "What maintenance tasks are required for this document?",
    "How do I replace the drive belt?",
    "What is the operating pressure range?",
    "Show me the spare parts table.",
    "What does ordering code MK311007 mean?",
    "Figure 3 shows the wiring diagram.",
    "What does the FWC system do?",
    "This is a safety concern.",
    "What is the difference between valve A and valve B?",
    "pump",
    "safety",
    "How do I troublshoot the pump?",
    "What is the presure range?",
    "Wie oft muss die Wartung durchgefuehrt werden?",
    "Was ist der Nenndruck der Pumpe?",
)


def _load_query_texts(truth_set_path: Path | None) -> list[str]:
    from src.application.evaluation import (
        DEFAULT_RETRIEVAL_TRUTH_SET_PATH,
        RetrievalTruthSetLoader,
    )

    resolved_path = truth_set_path or DEFAULT_RETRIEVAL_TRUTH_SET_PATH
    if not resolved_path.exists():
        print(
            f"Truth-set file not found at {resolved_path} (gitignored corpus "
            "fixture) -- using the built-in synthetic query set instead."
        )
        return list(_SYNTHETIC_QUERY_SET)

    dataset = RetrievalTruthSetLoader().load(resolved_path)
    query_texts = [case.query_text for case in dataset.cases if case.query_text]
    print(f"Loaded {len(query_texts)} queries from {resolved_path}.")
    return query_texts


def replay(query_texts: Sequence[str], *, output_path: Path) -> int:
    from src.application.workflows.retrieval.query_analysis.retrieval_query_intent_inferer import (
        RetrievalQueryIntentInferer,
    )
    from src.domain.retrieval import RetrievalQuery

    output_path.parent.mkdir(parents=True, exist_ok=True)

    inferer_logger = logging.getLogger(
        "src.application.workflows.retrieval.query_analysis.retrieval_query_intent_inferer"
    )
    original_level = inferer_logger.level
    original_propagate = inferer_logger.propagate
    handler = logging.FileHandler(output_path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))

    inferer_logger.addHandler(handler)
    inferer_logger.setLevel(logging.INFO)
    inferer_logger.propagate = False
    try:
        inferer = RetrievalQueryIntentInferer()
        for index, query_text in enumerate(query_texts, start=1):
            query = RetrievalQuery(query_id=f"replay_{index}", query_text=query_text)
            inferer.infer(query)
    finally:
        inferer_logger.removeHandler(handler)
        handler.close()
        inferer_logger.setLevel(original_level)
        inferer_logger.propagate = original_propagate

    return len(query_texts)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--truth-set",
        type=Path,
        default=None,
        help="Optional retrieval truth-set markdown path (defaults to the gitignored corpus path).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Where to write the synthetic log (default: {DEFAULT_OUTPUT_PATH}).",
    )
    args = parser.parse_args(argv)

    query_texts = _load_query_texts(args.truth_set)
    count = replay(query_texts, output_path=args.output)
    print(f"Replayed {count} queries -> {args.output}")
    print(
        f"Run: python scripts/report_retrieval_intent_fallback_rate.py "
        f"--log-file {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
