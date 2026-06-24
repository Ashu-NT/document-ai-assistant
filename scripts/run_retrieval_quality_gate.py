from __future__ import annotations

"""
Run the retrieval quality gate against a benchmark report JSON file.

Usage:
    python scripts/run_retrieval_quality_gate.py outputs/evaluation/retrieval/retrieval_benchmark_report.json
    python scripts/run_retrieval_quality_gate.py outputs/evaluation/retrieval/retrieval_benchmark_report.json --thresholds src/config/evaluation/retrieval_thresholds.yaml
    python scripts/run_retrieval_quality_gate.py outputs/evaluation/retrieval/retrieval_benchmark_report.json --strict
"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
for _root in (PROJECT_ROOT, SRC_ROOT):
    _root_str = str(_root)
    if _root_str not in sys.path:
        sys.path.insert(0, _root_str)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Check a retrieval benchmark report against quality thresholds."
    )
    parser.add_argument(
        "report",
        metavar="REPORT_JSON",
        help="Path to the benchmark report JSON file.",
    )
    parser.add_argument(
        "--thresholds",
        metavar="YAML",
        default=None,
        help="Path to thresholds YAML (default: src/config/evaluation/retrieval_thresholds.yaml).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (not used yet; reserved for future use).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON.",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"ERROR: report file not found: {report_path}", file=sys.stderr)
        return 2

    try:
        report_data = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: failed to read report: {exc}", file=sys.stderr)
        return 2

    from src.application.evaluation.retrieval import RetrievalQualityGate  # noqa: WPS433

    gate = RetrievalQualityGate(thresholds_path=args.thresholds)
    result = gate.check(report_data)

    if args.json:
        import dataclasses  # noqa: WPS433

        output = {
            "passed": result.passed,
            "violations": [dataclasses.asdict(v) for v in result.violations],
            "checked_metrics": result.checked_metrics,
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.summary())

    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
