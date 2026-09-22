from __future__ import annotations

"""
Run the fast golden-regression tier: every document in the golden corpus
manifest (src/application/evaluation/corpus/golden_corpus_manifest.py)
through the real production parsing path (Parsed Artifact Store ->
ParsingWorkflow -> structural expectations -> section/chunk invariants ->
cross-reference expectations), writing a JSON + Markdown report.

Does not run classification, extraction, embedding, or retrieval - see
outputs/architecture/golden_evaluation_corpus_architecture_investigation.md.

Usage:
    python scripts/run_golden_fast_regression.py [--cached-only] [--output-dir <path>]
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
for _import_root in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    _text = str(_import_root)
    if _text not in sys.path:
        sys.path.insert(0, _text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the fast golden-regression tier against real parsing output."
    )
    parser.add_argument(
        "--cached-only",
        action="store_true",
        help=(
            "Only use already-cached Parsed Artifacts; a cache miss is "
            "recorded as an explicit outcome instead of running real "
            "Docling conversion."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to write the JSON/Markdown report to.",
    )
    return parser.parse_args()


_args = parse_args()

from src.application.evaluation.golden import (  # noqa: E402
    run_fast_golden_regression,
)
from src.application.reporting.golden_evaluation import (  # noqa: E402
    GoldenEvaluationReportWriter,
)
from src.bootstrap.startup import bootstrap_application  # noqa: E402


def print_status(message: str) -> None:
    print(f"[golden-fast-regression] {message}", flush=True)


def main() -> int:
    bootstrap_application()

    print_status("Running fast golden regression...")
    report = run_fast_golden_regression(allow_real_parsing=not _args.cached_only)

    output_dir = (
        Path(_args.output_dir).expanduser().resolve()
        if _args.output_dir
        else (PROJECT_ROOT / "outputs" / "evaluation" / "golden")
    )
    writer = GoldenEvaluationReportWriter()
    json_path = writer.write_json(report, output_dir / "golden_evaluation_report.json")
    markdown_path = writer.write_markdown(
        report, output_dir / "golden_evaluation_report.md"
    )

    print_status(
        f"corpus: expected={report.corpus_coverage.expected} "
        f"available={report.corpus_coverage.available} "
        f"evaluated={report.corpus_coverage.evaluated}"
    )
    print_status(
        f"structural: passed={report.structural_passed_count} "
        f"failed={report.structural_failed_count}"
    )
    print_status(f"chunk invariant failures: {report.chunk_invariant_failure_count}")
    print_status(f"reports written to {json_path} and {markdown_path}")

    not_evaluated = report.documents_not_evaluated
    if not_evaluated:
        print_status(
            f"{len(not_evaluated)} document(s) NOT evaluated: "
            f"{[o.alias for o in not_evaluated]}"
        )

    ok = (
        report.structural_failed_count == 0
        and report.corpus_coverage.evaluated == report.corpus_coverage.available
    )
    print_status("OK" if ok else "FAILURES OR INCOMPLETE COVERAGE PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
