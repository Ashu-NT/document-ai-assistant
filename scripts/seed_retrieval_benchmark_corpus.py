from __future__ import annotations

"""
Seed the retrieval benchmark corpus with the existing workflow chain only.

Usage:
    python scripts/seed_retrieval_benchmark_corpus.py
    python scripts/seed_retrieval_benchmark_corpus.py --truth-set TestDoc/retrieval_truth_set.md
"""

import argparse
import json
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for import_root in (PROJECT_ROOT, SRC_ROOT):
    import_root_text = str(import_root)
    if import_root_text not in sys.path:
        sys.path.insert(0, import_root_text)

from qdrant_client import QdrantClient  # noqa: E402

from src.application.evaluation.retrieval import (  # noqa: E402
    DEFAULT_RETRIEVAL_TRUTH_SET_PATH,
    RetrievalBenchmarkCorpusSeeder,
)
from src.application.orchestrator.ingestion import build_ingestion_runtime  # noqa: E402
from src.config.paths import ensure_directory, resolve_project_path  # noqa: E402
from src.config.settings import (  # noqa: E402
    docling_settings,
    ocr_settings,
    storage_settings,
)
from src.infrastructure.db.base import Base  # noqa: E402,F401
from src.infrastructure.db.orm_models import __all__ as _orm_models_loaded  # noqa: E402,F401


@dataclass(slots=True)
class CorpusSeederRuntime:
    seeder: RetrievalBenchmarkCorpusSeeder
    qdrant_client: QdrantClient | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Seed the retrieval benchmark corpus using the existing parsing, "
            "classification, chunk finalization, question generation, and "
            "embedding workflows."
        )
    )
    parser.add_argument(
        "--truth-set",
        default=str(DEFAULT_RETRIEVAL_TRUTH_SET_PATH),
        help="Optional truth-set markdown path.",
    )
    parser.add_argument(
        "--input-dir",
        help=(
            "Optional directory containing the benchmark PDFs. "
            "Defaults to the truth-set parent directory."
        ),
    )
    parser.add_argument(
        "--output",
        help=(
            "Optional manifest output path. Defaults to "
            "outputs/evaluation/retrieval/benchmark_corpus_manifest.json"
        ),
    )
    parser.add_argument(
        "--force-reparse",
        action="store_true",
        help=(
            "Reparse and replace full persisted document graphs when an input file "
            "already exists instead of reusing the stored graph."
        ),
    )
    return parser.parse_args()


def print_status(message: str) -> None:
    print(f"[seed-retrieval-corpus] {message}", flush=True)


def print_runtime_ocr_configuration() -> None:
    print_status(
        "Docling pipeline: "
        f"pdf_backend={docling_settings.pdf_backend}, "
        f"device={docling_settings.accelerator_device}, "
        f"images_scale={docling_settings.images_scale}, "
        f"table_structure={docling_settings.enable_table_structure}, "
        f"num_threads={docling_settings.num_threads}, "
        f"layout_batch_size={docling_settings.layout_batch_size}, "
        f"table_batch_size={docling_settings.table_batch_size}"
    )
    print_status(
        "Docling OCR: "
        f"enabled={docling_settings.enable_ocr}, "
        f"engine={docling_settings.ocr_engine}, "
        f"batch_size={docling_settings.ocr_batch_size}"
    )
    print_status(
        "Provider OCR: "
        f"enabled={ocr_settings.enabled}, "
        f"provider={ocr_settings.provider}"
    )
    print_status(
        "OCR fallback: "
        f"asset={ocr_settings.asset_enabled}, "
        f"page_fallback={ocr_settings.page_fallback_enabled}, "
        f"region_fallback={ocr_settings.region_fallback_enabled}, "
        f"trace={ocr_settings.trace_enabled}"
    )


def resolve_path(value: str | None) -> Path | None:
    if value is None:
        return None
    return resolve_project_path(value).expanduser().resolve()


def default_output_path() -> Path:
    return (
        storage_settings.evaluation_output_path
        / "retrieval"
        / "benchmark_corpus_manifest.json"
    ).resolve()


def build_corpus_seeder() -> CorpusSeederRuntime:
    """Build the corpus seeder on top of the canonical ingestion orchestrator.

    All ingestion dependency wiring (parsing, classification, extraction,
    identifier promotion/scanning, embedding, vector storage) lives in
    `src.application.orchestrator.ingestion.build_ingestion_runtime`. This
    function only adds the benchmark-specific wrapping (`RetrievalBenchmarkCorpusSeeder`).
    """
    runtime = build_ingestion_runtime()

    return CorpusSeederRuntime(
        seeder=RetrievalBenchmarkCorpusSeeder(
            ingestion_workflow=runtime.ingestion_workflow,
            duplicate_detection_service=runtime.duplicate_detection_service,
            document_lookup_service=runtime.document_lookup_service,
            classification_service=runtime.classification_service,
            document_classification_workflow=runtime.document_classification_workflow,
            unit_of_work=runtime.unit_of_work,
            embedding_model=runtime.embedding_model,
            vector_collection=runtime.vector_collection,
        ),
        qdrant_client=runtime.qdrant_client,
    )


def main() -> int:
    args = parse_args()
    runtime: CorpusSeederRuntime | None = None
    seeder: RetrievalBenchmarkCorpusSeeder | None = None
    truth_set_path = resolve_path(args.truth_set)
    input_directory = resolve_path(args.input_dir)
    output_path = resolve_path(args.output) or default_output_path()
    ensure_directory(output_path.parent)

    print_status(f"Truth set path: {truth_set_path}")
    if input_directory is None:
        print_status("Input directory: derived from the truth-set parent directory")
    else:
        print_status(f"Input directory: {input_directory}")
    print_status(f"Manifest output path: {output_path}")
    print_status(
        "Duplicate handling: "
        + (
            "force reparse existing documents"
            if args.force_reparse
            else "reuse existing persisted graphs when file hash matches"
        )
    )
    print_runtime_ocr_configuration()
    print_status("Building corpus seeder runtime...")
    runtime = build_corpus_seeder()
    seeder = runtime.seeder
    print_status("Corpus seeder runtime ready.")

    try:
        print_status("Starting retrieval benchmark corpus seeding...")
        manifest = seeder.seed_corpus(
            truth_set_path=truth_set_path,
            input_directory=input_directory,
            force_reparse_existing=args.force_reparse,
            progress_callback=print_status,
        )
        print_status(
            f"Writing manifest for {manifest.document_count} document(s)..."
        )
        output_path.write_text(
            json.dumps(manifest.to_dict(), indent=2),
            encoding="utf-8",
        )
        print_status("Corpus manifest written successfully.")
    except Exception:
        unit_of_work = getattr(seeder, "unit_of_work", None)
        if unit_of_work is not None:
            unit_of_work.rollback()
        traceback.print_exc()
        return 1
    finally:
        unit_of_work = getattr(seeder, "unit_of_work", None)
        session = getattr(unit_of_work, "session", None)
        if session is not None:
            session.close()
        close_quietly(getattr(runtime, "qdrant_client", None))

    print(output_path)
    return 0


def close_quietly(resource) -> None:
    if resource is None:
        return

    close = getattr(resource, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            return


if __name__ == "__main__":
    raise SystemExit(main())
