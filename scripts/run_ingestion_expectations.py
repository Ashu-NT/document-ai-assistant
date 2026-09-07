from __future__ import annotations

"""
Run every structural-expectations case in the ingestion truth set
(TestDoc/retrieval_truth_set.md, section "# 7. Structural Expectations")
through the real production parsing path (Docling conversion -> canonical
normalization -> document graph build, including fuzzy/native cross-
reference reconciliation) and report pass/fail per labeled assertion.

Does not persist anything to a database and does not run embedding,
classification, or extraction -- same scope as
ingest_document_cross_reference_report.py, which this script's parsing
invocation is deliberately kept consistent with. `expected_document_type`
on a case is accepted by the loader but not evaluated here (classification
is a separate downstream stage not run by this script).

Usage:
    python scripts/run_ingestion_expectations.py [--truth-set <path>] [--output <path>]
"""

import argparse
import hashlib
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
for _import_root in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    _text = str(_import_root)
    if _text not in sys.path:
        sys.path.insert(0, _text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run ingestion structural-expectations cases against real parsing output."
    )
    parser.add_argument("--truth-set", default=None, help="Path to the truth-set markdown file.")
    parser.add_argument("--output", default=None, help="Path to write the markdown report to.")
    return parser.parse_args()


_args = parse_args()

# Must happen before any `from src...` import: settings are pydantic
# BaseSettings singletons instantiated at module-import time.
os.environ.setdefault("CHUNK_CROSS_REFERENCE_PDF_LINKS_ENABLED", "true")
os.environ.setdefault("CHUNK_CROSS_REFERENCE_DETECTION_ENABLED", "true")

from src.application.evaluation.ingestion.ingestion_expectation_evaluator import (  # noqa: E402
    IngestionExpectationEvaluator,
)
from src.application.evaluation.ingestion.loaders.ingestion_truth_set_loader import (  # noqa: E402
    IngestionTruthSetLoader,
)
from src.application.evaluation.ingestion.models.ingestion_expectation_case import (  # noqa: E402
    IngestionExpectationCase,
)
from src.application.evaluation.ingestion.models.ingestion_expectation_result import (  # noqa: E402
    IngestionAssertionResult,
    IngestionExpectationCaseResult,
)
from src.application.orchestrator.ingestion.parsing_runtime_builder import (  # noqa: E402
    build_parsing_runtime,
)
from src.bootstrap.startup import bootstrap_application  # noqa: E402
from src.config.paths import ensure_directory  # noqa: E402
from src.shared.ids import IdGenerator, IdPrefix  # noqa: E402


def print_status(message: str) -> None:
    print(f"[ingestion-expectations] {message}", flush=True)


def compute_hashes(file_path: Path) -> tuple[str, str]:
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    file_hash = digest.hexdigest()
    return file_hash, file_hash


def resolve_document_path(document_path: Path) -> Path:
    if document_path.is_absolute():
        return document_path
    return (PROJECT_ROOT / document_path).resolve()


def run_case(
    case: IngestionExpectationCase,
    *,
    evaluator: IngestionExpectationEvaluator,
) -> IngestionExpectationCaseResult:
    input_path = resolve_document_path(case.document_path)
    if not input_path.exists():
        return IngestionExpectationCaseResult(
            case_id=case.case_id,
            assertions=[
                IngestionAssertionResult(
                    name="document_exists",
                    expected=str(input_path),
                    actual="file not found",
                    passed=False,
                )
            ],
        )

    id_generator = IdGenerator()
    document_id = id_generator.new_id(IdPrefix.DOCUMENT)
    file_hash, content_hash = compute_hashes(input_path)
    parsing_workflow, _document_graph_builder = build_parsing_runtime(
        id_generator=id_generator
    )

    print_status(f"[{case.case_id}] parsing {input_path} ...")
    started_at = time.perf_counter()
    result = parsing_workflow.parse(
        file_path=str(input_path),
        file_hash=file_hash,
        content_hash=content_hash,
        document_id=document_id,
        progress_callback=print_status,
    )
    elapsed_seconds = time.perf_counter() - started_at
    print_status(f"[{case.case_id}] parsed in {elapsed_seconds:.1f}s")

    return evaluator.evaluate(case=case, document_graph=result.document_graph)


def build_report(results: list[IngestionExpectationCaseResult]) -> str:
    lines = ["# Ingestion Expectations Report", ""]
    total_assertions = sum(len(result.assertions) for result in results)
    total_passed = sum(
        1 for result in results for assertion in result.assertions if assertion.passed
    )
    lines.append(f"- cases: `{len(results)}`")
    lines.append(f"- cases passed: `{sum(1 for result in results if result.passed)}`")
    lines.append(f"- assertions: `{total_passed}/{total_assertions}` passed")
    lines.append("")

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"## {result.case_id} -- {status}")
        lines.append("")
        lines.append("| assertion | expected | actual | status |")
        lines.append("| --- | --- | --- | --- |")
        for assertion in result.assertions:
            mark = "pass" if assertion.passed else "**FAIL**"
            lines.append(
                f"| {assertion.name} | {assertion.expected} | {assertion.actual} | {mark} |"
            )
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    bootstrap_application()
    cases = IngestionTruthSetLoader().load(_args.truth_set)
    evaluator = IngestionExpectationEvaluator()

    results = [run_case(case, evaluator=evaluator) for case in cases]

    output_path = (
        Path(_args.output).expanduser().resolve()
        if _args.output
        else (PROJECT_ROOT / "outputs" / "evaluation" / "ingestion" / "ingestion_expectations_report.md")
    )
    ensure_directory(output_path.parent)
    output_path.write_text(build_report(results), encoding="utf-8")

    all_passed = all(result.passed for result in results)
    print_status(f"Report written to {output_path}")
    print_status("OK" if all_passed else "FAILURES PRESENT")
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
