from __future__ import annotations

"""
Run the retrieval benchmark against the already-seeded corpus.

Usage:
    python scripts/run_retrieval_benchmark.py
    python scripts/run_retrieval_benchmark.py --subset identifier
    python scripts/run_retrieval_benchmark.py --truth-set TestDoc/retrieval_truth_set.md
"""

import argparse
import copy
import json
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for import_root in (PROJECT_ROOT, SRC_ROOT):
    import_root_text = str(import_root)
    if import_root_text not in sys.path:
        sys.path.insert(0, import_root_text)

from src.application.evaluation import (  # noqa: E402
    DEFAULT_RETRIEVAL_TRUTH_SET_PATH,
    RetrievalBenchmarkCorpusManifestLoader,
    RetrievalBenchmarkDataset,
    RetrievalBenchmarkDatasetResolver,
    RetrievalBenchmarkEvaluator,
    RetrievalBenchmarkReport,
    RetrievalBenchmarkReportWriter,
    RetrievalTruthSetLoader,
)
from src.config.paths import resolve_project_path  # noqa: E402
from src.shared.exceptions import ApplicationError, SchemaValidationError  # noqa: E402

_SUBSET_FULL = "full"
_SUBSET_IDENTIFIER = "identifier"
_SUBSET_SEMANTIC = "semantic"
_SUBSET_CHOICES = (
    _SUBSET_FULL,
    _SUBSET_IDENTIFIER,
    _SUBSET_SEMANTIC,
)
_BENCHMARK_FAILURE_EXIT_CODE = 2


@dataclass(slots=True)
class BenchmarkRuntime:
    truth_set_loader: RetrievalTruthSetLoader
    manifest_loader: RetrievalBenchmarkCorpusManifestLoader
    dataset_resolver: RetrievalBenchmarkDatasetResolver
    evaluator: RetrievalBenchmarkEvaluator
    report_writer: RetrievalBenchmarkReportWriter
    workflow: Any
    session: Any = None


@dataclass(slots=True)
class BenchmarkRunResult:
    subset: str
    selected_case_count: int
    failed_case_count: int
    json_output_path: Path
    markdown_output_path: Path
    report: RetrievalBenchmarkReport


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the retrieval benchmark against the final persisted seeded corpus."
        )
    )
    parser.add_argument(
        "--truth-set",
        default=str(DEFAULT_RETRIEVAL_TRUTH_SET_PATH),
        help="Optional retrieval truth-set markdown path.",
    )
    parser.add_argument(
        "--manifest",
        help=(
            "Optional benchmark corpus manifest path. Defaults to "
            "outputs/evaluation/retrieval/benchmark_corpus_manifest.json"
        ),
    )
    parser.add_argument(
        "--subset",
        choices=_SUBSET_CHOICES,
        default=_SUBSET_FULL,
        help="Benchmark subset to run.",
    )
    parser.add_argument(
        "--output-dir",
        help=(
            "Optional output directory for benchmark JSON/Markdown reports. "
            "Defaults to outputs/evaluation/retrieval"
        ),
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def resolve_path(value: str | None) -> Path | None:
    if value is None:
        return None
    return resolve_project_path(value).expanduser().resolve()


def default_manifest_path() -> Path:
    from src.config.settings import storage_settings  # noqa: WPS433

    return (
        storage_settings.evaluation_output_path
        / "retrieval"
        / "benchmark_corpus_manifest.json"
    ).resolve()


def default_output_directory() -> Path:
    from src.config.settings import storage_settings  # noqa: WPS433

    return (storage_settings.evaluation_output_path / "retrieval").resolve()


def ensure_manifest_exists(
    *,
    manifest_path: Path,
    truth_set_argument: str,
) -> None:
    if manifest_path.exists():
        return

    suggested_command = (
        "python scripts/seed_retrieval_benchmark_corpus.py "
        f"--truth-set {truth_set_argument}"
    )
    raise SchemaValidationError(
        "Retrieval benchmark corpus manifest file not found. "
        "Seed the retrieval benchmark corpus first, or pass --manifest to an "
        "existing benchmark corpus manifest.",
        details={
            "path": str(manifest_path),
            "suggested_seed_command": suggested_command,
            "suggested_next_step": (
                "Run the seed script once before running the retrieval benchmark."
            ),
        },
    )


def build_benchmark_runtime() -> BenchmarkRuntime:
    from qdrant_client import QdrantClient  # noqa: WPS433

    from src.application.services.ai import EmbeddingService  # noqa: WPS433
    from src.application.services.document import DocumentLookupService  # noqa: WPS433
    from src.application.services.retrieval import HybridRetrievalService  # noqa: WPS433
    from src.application.validation.retrieval import RetrievalQueryValidator  # noqa: WPS433
    from src.application.workflows.retrieval import (  # noqa: WPS433
        RetrievalContextExpander,
        RetrievalWorkflow,
    )
    from src.bootstrap.startup import bootstrap_application  # noqa: WPS433
    from src.config.settings import (  # noqa: WPS433
        embedding_settings,
        qdrant_settings,
    )
    from src.infrastructure.ai.embeddings import BgeEmbeddingProvider  # noqa: WPS433
    from src.infrastructure.db.base import Base  # noqa: WPS433
    from src.infrastructure.db.orm_models import (  # noqa: WPS433,F401
        __all__ as _orm_models_loaded,
    )
    from src.infrastructure.db.session import SessionLocal, engine  # noqa: WPS433
    from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork  # noqa: WPS433
    from src.infrastructure.retrieval.keyword import SqlKeywordIndex  # noqa: WPS433
    from src.infrastructure.retrieval.rerankers import NoOpReranker  # noqa: WPS433
    from src.infrastructure.retrieval.vector import QdrantVectorStore  # noqa: WPS433
    from src.shared.ids import IdGenerator  # noqa: WPS433

    bootstrap_application()
    Base.metadata.create_all(engine)

    session = SessionLocal()
    unit_of_work = SqlAlchemyUnitOfWork(session)
    query_validator = RetrievalQueryValidator()
    embedding_provider = BgeEmbeddingProvider(
        model_name=embedding_settings.model_name,
    )
    vector_store = QdrantVectorStore(
        client=_create_qdrant_client(QdrantClient),
        mapping_repository=unit_of_work.vector_mappings,
        collection_name=qdrant_settings.collection,
        embedding_model=embedding_settings.model_name,
        query_embedding_provider=embedding_provider,
    )
    document_lookup_service = DocumentLookupService(unit_of_work.documents)
    retrieval_service = HybridRetrievalService(
        keyword_index=SqlKeywordIndex(unit_of_work.keyword_index),
        id_generator=IdGenerator(),
        retrieval_query_validator=query_validator,
        vector_store=vector_store,
        reranker=NoOpReranker(),
    )
    workflow = RetrievalWorkflow(
        retrieval_service=retrieval_service,
        query_validator=query_validator,
        context_expander=RetrievalContextExpander(
            document_lookup_service=document_lookup_service,
        ),
    )
    return BenchmarkRuntime(
        truth_set_loader=RetrievalTruthSetLoader(),
        manifest_loader=RetrievalBenchmarkCorpusManifestLoader(),
        dataset_resolver=RetrievalBenchmarkDatasetResolver(
            document_lookup_service=document_lookup_service,
        ),
        evaluator=RetrievalBenchmarkEvaluator(),
        report_writer=RetrievalBenchmarkReportWriter(),
        workflow=workflow,
        session=session,
    )


def _create_qdrant_client(qdrant_client_class):
    from src.config.settings import qdrant_settings  # noqa: WPS433

    if qdrant_settings.mode.lower() == "local":
        return qdrant_client_class(path=str(qdrant_settings.storage_path))

    return qdrant_client_class(
        host=qdrant_settings.host,
        port=qdrant_settings.port,
    )


def run_benchmark(
    *,
    runtime: BenchmarkRuntime,
    truth_set_path: Path | str | None,
    manifest_path: Path | str,
    subset: str,
    output_directory: Path | str,
    evaluation_top_k: int,
) -> BenchmarkRunResult:
    dataset = runtime.truth_set_loader.load(truth_set_path)
    selected_dataset = select_subset_dataset(
        dataset,
        subset=subset,
        evaluation_top_k=evaluation_top_k,
    )
    manifest = runtime.manifest_loader.load(manifest_path)
    resolved_dataset = runtime.dataset_resolver.resolve_dataset(
        selected_dataset,
        manifest,
    )
    report = runtime.evaluator.evaluate(
        runtime.workflow,
        resolved_dataset,
    )
    json_output_path, markdown_output_path = resolve_output_paths(
        output_directory=Path(output_directory),
        subset=subset,
    )
    runtime.report_writer.write_json(report, json_output_path)
    runtime.report_writer.write_markdown(report, markdown_output_path)

    return BenchmarkRunResult(
        subset=subset,
        selected_case_count=resolved_dataset.case_count,
        failed_case_count=count_failed_cases(report),
        json_output_path=json_output_path,
        markdown_output_path=markdown_output_path,
        report=report,
    )


def select_subset_dataset(
    dataset: RetrievalBenchmarkDataset,
    *,
    subset: str,
    evaluation_top_k: int,
) -> RetrievalBenchmarkDataset:
    if subset == _SUBSET_IDENTIFIER:
        selected_cases = dataset.identifier_focused_cases
    elif subset == _SUBSET_SEMANTIC:
        selected_cases = dataset.semantic_procedure_cases
    else:
        selected_cases = dataset.canonical_cases

    if not selected_cases:
        raise SchemaValidationError(
            "Retrieval benchmark subset did not contain any cases.",
            details={
                "subset": subset,
                "source_path": str(dataset.source_path),
            },
        )

    copied_cases = copy.deepcopy(selected_cases)
    for case in copied_cases:
        if case.query is not None:
            case.query.top_k = max(case.query.top_k, evaluation_top_k)

    return RetrievalBenchmarkDataset(
        source_path=dataset.source_path,
        cases=copied_cases,
        identifier_subset_definition=dataset.identifier_subset_definition,
        semantic_procedure_subset_definition=(
            dataset.semantic_procedure_subset_definition
        ),
    )


def resolve_output_paths(
    *,
    output_directory: Path,
    subset: str,
) -> tuple[Path, Path]:
    report_stem = (
        "retrieval_benchmark_report"
        if subset == _SUBSET_FULL
        else f"retrieval_benchmark_{subset}_report"
    )
    return (
        (output_directory / f"{report_stem}.json").resolve(),
        (output_directory / f"{report_stem}.md").resolve(),
    )


def count_failed_cases(report: RetrievalBenchmarkReport) -> int:
    return sum(
        1
        for case_result in report.case_results
        if not case_result.meets_expected_rank_target
    )


def benchmark_evaluation_top_k() -> int:
    from src.config.settings import retrieval_settings  # noqa: WPS433

    return max(retrieval_settings.final_retrieval_top_k, 10)


def close_runtime(runtime: BenchmarkRuntime | None) -> None:
    if runtime is None:
        return
    session = getattr(runtime, "session", None)
    if session is not None:
        session.close()


def format_error_details(details: dict[str, Any] | None) -> str:
    return json.dumps(details or {}, indent=2)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    runtime: BenchmarkRuntime | None = None

    try:
        truth_set_path = resolve_path(args.truth_set)
        manifest_path = resolve_path(args.manifest) or default_manifest_path()
        output_directory = resolve_path(args.output_dir) or default_output_directory()
        ensure_manifest_exists(
            manifest_path=manifest_path,
            truth_set_argument=args.truth_set,
        )

        runtime = build_benchmark_runtime()
        result = run_benchmark(
            runtime=runtime,
            truth_set_path=truth_set_path,
            manifest_path=manifest_path,
            subset=args.subset,
            output_directory=output_directory,
            evaluation_top_k=benchmark_evaluation_top_k(),
        )

        print(f"subset: {result.subset}")
        print(f"case_count: {result.selected_case_count}")
        print(f"failed_case_count: {result.failed_case_count}")
        print(result.json_output_path)
        print(result.markdown_output_path)

        if result.failed_case_count > 0:
            return _BENCHMARK_FAILURE_EXIT_CODE

        return 0
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (SchemaValidationError, ApplicationError) as exc:
        print(f"{exc.error_code}: {exc.message}", file=sys.stderr)
        if exc.details:
            print(format_error_details(exc.details), file=sys.stderr)
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    finally:
        close_runtime(runtime)


if __name__ == "__main__":
    raise SystemExit(main())
