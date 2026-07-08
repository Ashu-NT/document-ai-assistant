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
from src.application.evaluation.retrieval.benchmarking.corpus.models.retrieval_benchmark_corpus_manifest import (  # noqa: E402
    RetrievalBenchmarkCorpusManifest,
)
from src.application.orchestrator.ingestion import build_ingestion_runtime  # noqa: E402
from src.application.workflows.parsing.ocr import (  # noqa: E402
    resolve_parsing_ocr_policy,
)
from src.application.workflows.extraction.candidates import (  # noqa: E402
    ExtractionCandidateSelector,
)
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
    ocr_policy = resolve_parsing_ocr_policy()
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
        f"enabled={ocr_policy.docling_ocr_enabled}, "
        f"engine={docling_settings.ocr_engine}, "
        f"batch_size={docling_settings.ocr_batch_size}"
    )
    print_status(
        "Provider OCR runtime: "
        f"requested={ocr_policy.provider_requested}, "
        f"enabled={ocr_policy.provider_runtime_enabled}, "
        f"provider={ocr_policy.provider_name}"
    )
    print_status(
        "Provider OCR stages: "
        f"asset={ocr_policy.asset_ocr_enabled}, "
        f"page_fallback={ocr_policy.page_fallback_enabled}, "
        f"region_fallback={ocr_policy.region_fallback_enabled}, "
        f"trace={ocr_settings.trace_enabled}"
    )


def print_chunk_classification_report(
    seeder: RetrievalBenchmarkCorpusSeeder,
    manifest: RetrievalBenchmarkCorpusManifest,
) -> None:
    """Per-chunk report: ChunkType + whether it was resolved by the
    deterministic scorer or the LLM fallback (chunk_type_source), plus
    what ExtractionCandidateSelector would narrow extraction to for that
    chunk (chunk_type/cross-signal candidates; candidate narrowing itself
    is not wired into ExtractionWorkflow by default, this is a preview of
    what it would select)."""
    selector = ExtractionCandidateSelector()

    for document in manifest.documents:
        chunks = seeder.document_lookup_service.list_chunks_by_document(
            document.document_id
        )
        chunks = sorted(chunks, key=lambda chunk: chunk.sequence_number)

        print_status(
            f"--- Chunk classification report: {document.file_name} "
            f"({document.document_id}, {len(chunks)} chunk(s)) ---"
        )

        source_counts: dict[str, int] = {}
        type_counts: dict[str, int] = {}
        candidate_counts: dict[str, int] = {}

        for chunk in chunks:
            candidates = sorted(
                entity_type.value
                for entity_type in selector.select_for_chunk(chunk)
            )
            is_narrowed = candidates != sorted(
                entity_type.value for entity_type in ExtractionCandidateSelector.all_types()
            )
            candidate_summary = ", ".join(candidates) if is_narrowed else "ALL (unnarrowed)"

            print_status(
                f"  chunk={chunk.chunk_id} "
                f"type={chunk.chunk_type.value} ({chunk.chunk_type_source}) "
                f"candidates=[{candidate_summary}]"
            )

            source_counts[chunk.chunk_type_source] = (
                source_counts.get(chunk.chunk_type_source, 0) + 1
            )
            type_counts[chunk.chunk_type.value] = (
                type_counts.get(chunk.chunk_type.value, 0) + 1
            )
            if is_narrowed:
                candidate_counts["narrowed"] = candidate_counts.get("narrowed", 0) + 1
            else:
                candidate_counts["unnarrowed"] = candidate_counts.get("unnarrowed", 0) + 1

        print_status(
            f"  Summary: chunk_type_source={source_counts}, "
            f"chunk_type={type_counts}, candidate_narrowing={candidate_counts}"
        )


def print_semantic_linking_report(
    seeder: RetrievalBenchmarkCorpusSeeder,
    manifest: RetrievalBenchmarkCorpusManifest,
) -> None:
    """Per-document report of the `SemanticRelationship` rows produced by
    `SemanticLinkingWorkflow` (gated by `SEMANTIC_LINKING_ENABLED`, run
    automatically by `IngestionWorkflow` right after extraction is saved).

    Prints nothing meaningful when the flag is off: `extraction_service`
    is still queried, but `list_semantic_relationships` simply returns an
    empty list since the workflow never ran.
    """
    if seeder.extraction_service is None:
        print_status(
            "Semantic linking report skipped: seeder has no extraction_service wired."
        )
        return

    for document in manifest.documents:
        relationships = seeder.extraction_service.list_semantic_relationships(
            document.document_id
        )

        print_status(
            f"--- Semantic linking report: {document.file_name} "
            f"({document.document_id}, {len(relationships)} relationship(s)) ---"
        )

        if not relationships:
            continue

        type_counts: dict[str, int] = {}
        status_counts: dict[str, int] = {}
        evidence_counts: dict[str, int] = {}

        for relationship in sorted(
            relationships, key=lambda r: r.relationship_type.value
        ):
            print_status(
                f"  {relationship.relationship_type.value}: "
                f"{relationship.source_entity_type.value}:{relationship.source_entity_id} "
                f"-> {relationship.target_entity_type.value}:{relationship.target_entity_id} "
                f"(status={relationship.status.value}, "
                f"confidence={relationship.confidence_score:.2f}, "
                f"evidence={relationship.evidence})"
            )

            type_counts[relationship.relationship_type.value] = (
                type_counts.get(relationship.relationship_type.value, 0) + 1
            )
            status_counts[relationship.status.value] = (
                status_counts.get(relationship.status.value, 0) + 1
            )
            if relationship.evidence:
                evidence_counts[relationship.evidence] = (
                    evidence_counts.get(relationship.evidence, 0) + 1
                )

        print_status(
            f"  Summary: relationship_type={type_counts}, status={status_counts}, "
            f"evidence={evidence_counts}"
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
            extraction_service=runtime.extraction_service,
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
        print_chunk_classification_report(seeder, manifest)
        print_semantic_linking_report(seeder, manifest)
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
