from __future__ import annotations

"""
Run a real ParsingWorkflow.parse() against one PDF and check the measured
per-stage durations (Docling conversion, canonical normalization, graph
build, total) against configured performance thresholds.

This is the P2 "explicit performance regression tracking" tool: run it
against a fixed reference document (ideally a large manual and, separately, a
scanned/image-heavy PDF) on a schedule or before/after a Docling/normalization
change, and compare results over time.

Usage:
    python scripts/run_parsing_performance_gate.py TestDoc/large_manual.pdf
    python scripts/run_parsing_performance_gate.py TestDoc/scanned.pdf --thresholds src/config/evaluation/parsing_performance_thresholds.yaml
    python scripts/run_parsing_performance_gate.py TestDoc/large_manual.pdf --json
"""

import argparse
import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for import_root in (PROJECT_ROOT, SRC_ROOT):
    import_root_text = str(import_root)
    if import_root_text not in sys.path:
        sys.path.insert(0, import_root_text)

from src.application.evaluation.parsing import (  # noqa: E402
    ParsingPerformanceGate,
)
from src.application.orchestrator.ingestion import build_parsing_runtime  # noqa: E402
from src.shared.ids import IdGenerator  # noqa: E402


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Parse one PDF and check Docling conversion/normalization/graph "
            "build durations against performance thresholds."
        )
    )
    parser.add_argument(
        "input",
        metavar="INPUT_PDF",
        help="Path to the PDF to parse.",
    )
    parser.add_argument(
        "--thresholds",
        metavar="YAML",
        default=None,
        help=(
            "Path to thresholds YAML "
            "(default: src/config/evaluation/parsing_performance_thresholds.yaml)."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the result as JSON instead of a human-readable summary.",
    )
    return parser.parse_args(argv)


def _compute_file_hash(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def print_status(message: str) -> None:
    print(f"[parsing-performance-gate] {message}", flush=True)


def main(argv=None) -> int:
    args = parse_args(argv)
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        return 2

    parsing_workflow, _ = build_parsing_runtime(id_generator=IdGenerator())

    print_status(f"Parsing {input_path.name}...")
    result = parsing_workflow.parse(
        file_path=str(input_path),
        file_hash=_compute_file_hash(input_path),
        content_hash=None,
        progress_callback=print_status,
    )

    gate = ParsingPerformanceGate(thresholds_path=args.thresholds)
    gate_result = gate.check(result.stage_durations)

    if args.json:
        import json

        print(
            json.dumps(
                {
                    "input": str(input_path),
                    "passed": gate_result.passed,
                    "stage_durations": result.stage_durations,
                    "checked_stages": gate_result.checked_stages,
                    "violations": [
                        {
                            "stage": v.stage,
                            "actual_seconds": v.actual_seconds,
                            "threshold_seconds": v.threshold_seconds,
                            "message": v.message,
                        }
                        for v in gate_result.violations
                    ],
                },
                indent=2,
            )
        )
    else:
        print_status(f"Page count: {result.page_count}")
        print_status(gate_result.summary())

    return 0 if gate_result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
