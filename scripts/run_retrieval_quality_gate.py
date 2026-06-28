from __future__ import annotations

"""
Run the retrieval quality gate against a benchmark report JSON file.

Usage:
    python scripts/run_retrieval_quality_gate.py outputs/evaluation/retrieval/retrieval_benchmark_report.json
    python scripts/run_retrieval_quality_gate.py outputs/evaluation/retrieval/retrieval_benchmark_report.json --thresholds src/config/evaluation/retrieval_thresholds.yaml
    python scripts/run_retrieval_quality_gate.py outputs/evaluation/retrieval/retrieval_benchmark_report.json --strict
"""

import argparse
import sys

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
    from src.application.tools.evaluation import (  # noqa: WPS433
        RunQualityGateRequest,
        RunQualityGateTool,
    )

    result = RunQualityGateTool().run(
        RunQualityGateRequest(
            report_path=args.report,
            thresholds_path=args.thresholds,
        )
    )

    if args.json:
        import json  # noqa: WPS433

        print(json.dumps(result.data or result.diagnostics, indent=2))
    else:
        payload = result.data or result.diagnostics
        print(payload.get("summary", result.message or "Quality gate failed."))

    if result.success:
        return 0
    if result.error_code == "quality_gate_failed":
        return 1
    print(f"ERROR: {result.message}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
