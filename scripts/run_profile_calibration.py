from __future__ import annotations

"""
Run one labeled document through both the production (OLD, raw-occurrence)
structural-profile evidence formula and a candidate (NEW, ratio-based) one,
decided through the SAME unmodified StructuralProfileDecisionPolicy, and
record the comparison into an accumulating report so results build up
across every document supplied over time.

Does not modify any production scorer or decision-policy file, does not
persist anything to a database, and does not run classification/embedding --
same scope as run_ingestion_expectations.py, whose parsing invocation this
script's is kept consistent with.

Usage:
    python scripts/run_profile_calibration.py --input <path> --label <name> \\
        --expected-profile <manual|datasheet|drawing|report|certificate|default>
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
        description=(
            "Compare production vs. candidate structural-profile scoring "
            "for one labeled document."
        )
    )
    parser.add_argument("--input", required=True, help="Path to the document to parse.")
    parser.add_argument(
        "--label",
        required=True,
        help="Human-readable label for this document in the accumulating report.",
    )
    parser.add_argument(
        "--expected-profile",
        required=True,
        choices=["manual", "datasheet", "drawing", "report", "certificate", "default"],
        help="The ground-truth chunking profile for this document.",
    )
    return parser.parse_args()


_args = parse_args()

# Must happen before any `from src...` import: settings are pydantic
# BaseSettings singletons instantiated at module-import time.
os.environ.setdefault("CHUNK_CROSS_REFERENCE_PDF_LINKS_ENABLED", "true")
os.environ.setdefault("CHUNK_CROSS_REFERENCE_DETECTION_ENABLED", "true")

from src.application.evaluation.profile_calibration import (  # noqa: E402
    ProfileCalibrationReportStore,
    ProfileCalibrationRunner,
)
from src.application.orchestrator.ingestion.parsing_runtime_builder import (  # noqa: E402
    build_parsing_runtime,
)
from src.bootstrap.startup import bootstrap_application  # noqa: E402
from src.shared.ids import IdGenerator, IdPrefix  # noqa: E402


def print_status(message: str) -> None:
    print(f"[profile-calibration] {message}", flush=True)


def compute_hashes(file_path: Path) -> tuple[str, str]:
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    file_hash = digest.hexdigest()
    return file_hash, file_hash


def main() -> int:
    bootstrap_application()

    input_path = Path(_args.input).expanduser().resolve()
    if not input_path.exists():
        print_status(f"ERROR: input file not found: {input_path}")
        return 1

    id_generator = IdGenerator()
    document_id = id_generator.new_id(IdPrefix.DOCUMENT)
    file_hash, content_hash = compute_hashes(input_path)
    parsing_workflow, _document_graph_builder = build_parsing_runtime(
        id_generator=id_generator
    )

    print_status(f"parsing {input_path} ...")
    started_at = time.perf_counter()
    result = parsing_workflow.parse(
        file_path=str(input_path),
        file_hash=file_hash,
        content_hash=content_hash,
        document_id=document_id,
        progress_callback=print_status,
    )
    elapsed_seconds = time.perf_counter() - started_at
    print_status(f"parsed in {elapsed_seconds:.1f}s")

    graph = result.document_graph
    sections = sorted(
        graph.sections.values(), key=lambda section: section.sequence_number or 0
    )
    section_elements_by_id = {
        section.section_id: graph.get_section_elements(section.section_id)
        for section in sections
    }

    runner = ProfileCalibrationRunner()
    case_result = runner.run(
        document_label=_args.label,
        expected_profile=_args.expected_profile,
        document_title=graph.document.title,
        sections=sections,
        section_elements_by_id=section_elements_by_id,
    )

    store = ProfileCalibrationReportStore()
    all_results = store.upsert(case_result)

    print_status(
        f"OLD: selected={case_result.old.selected_profile} "
        f"gap={case_result.old.gap:.2f} confidence={case_result.old.confidence:.3f} "
        f"default={case_result.old.is_default} "
        f"{'CORRECT' if case_result.old_correct else 'WRONG'}"
    )
    print_status(
        f"NEW: selected={case_result.new.selected_profile} "
        f"gap={case_result.new.gap:.2f} confidence={case_result.new.confidence:.3f} "
        f"default={case_result.new.is_default} "
        f"{'CORRECT' if case_result.new_correct else 'WRONG'}"
    )
    old_correct = sum(1 for r in all_results if r.old_correct)
    new_correct = sum(1 for r in all_results if r.new_correct)
    print_status(
        f"Accumulated {len(all_results)} document(s): "
        f"OLD {old_correct}/{len(all_results)}, NEW {new_correct}/{len(all_results)}"
    )
    print_status(f"Report written to {store.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
