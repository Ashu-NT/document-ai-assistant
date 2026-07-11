from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from src.application.contracts import UnitOfWork
from src.application.evaluation.retrieval.benchmarking.corpus.models import (
    RetrievalBenchmarkCorpusDocument,
    RetrievalBenchmarkCorpusManifest,
)
from src.application.evaluation.retrieval.benchmarking.corpus.resolution.retrieval_benchmark_corpus_document_resolver import (
    resolve_corpus_document,
)
from src.application.evaluation.retrieval.benchmarking.corpus.retrieval_benchmark_corpus_document_builder import (
    build_manifest_document,
)
from src.application.evaluation.retrieval.benchmarking.corpus.retrieval_benchmark_corpus_hasher import (
    compute_hashes,
    format_file_size,
)
from src.application.evaluation.retrieval.benchmarking.corpus.retrieval_benchmark_seed_target_collector import (
    _CorpusSeedTarget,
    collect_seed_targets,
    resolve_input_directory,
)
from src.application.evaluation.retrieval.benchmarking.loaders import (
    RetrievalTruthSetLoader,
)
from src.application.services.classification import ClassificationService
from src.application.services.document import (
    DocumentLookupService,
    DuplicateDetectionService,
)
from src.application.services.extraction import ExtractionService
from src.application.workflows.classification import DocumentClassificationWorkflow
from src.application.workflows.ingestion import IngestionWorkflow
from src.shared.activity import ActivityContext
from src.shared.exceptions import ApplicationError
from src.shared.progress.progress_emitter import (
    emit_progress,
    progress_prefix,
)


class RetrievalBenchmarkCorpusSeeder:
    def __init__(
        self,
        *,
        ingestion_workflow: IngestionWorkflow,
        duplicate_detection_service: DuplicateDetectionService,
        document_lookup_service: DocumentLookupService,
        classification_service: ClassificationService,
        document_classification_workflow: DocumentClassificationWorkflow,
        truth_set_loader: RetrievalTruthSetLoader | None = None,
        unit_of_work: UnitOfWork | None = None,
        embedding_model: str | None = None,
        vector_collection: str | None = None,
        extraction_service: ExtractionService | None = None,
        hash_computer: Callable[[Path], tuple[str, str | None]] | None = None,
    ) -> None:
        self.ingestion_workflow = ingestion_workflow
        self.duplicate_detection_service = duplicate_detection_service
        self.document_lookup_service = document_lookup_service
        self.classification_service = classification_service
        self.document_classification_workflow = document_classification_workflow
        self.extraction_service = extraction_service
        self.truth_set_loader = truth_set_loader or RetrievalTruthSetLoader()
        self.unit_of_work = unit_of_work
        self.embedding_model = embedding_model
        self.vector_collection = vector_collection
        self.hash_computer = hash_computer or compute_hashes

    def seed_corpus(
        self,
        *,
        truth_set_path: Path | str | None = None,
        input_directory: Path | str | None = None,
        force_reparse_existing: bool = False,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> RetrievalBenchmarkCorpusManifest:
        emit_progress(
            progress_callback,
            "Loading retrieval benchmark truth set...",
        )
        dataset = self.truth_set_loader.load(truth_set_path)
        resolved_input_directory = resolve_input_directory(
            input_directory=input_directory,
            dataset=dataset,
        )
        emit_progress(
            progress_callback,
            f"Using input directory: {resolved_input_directory}",
        )
        emit_progress(
            progress_callback,
            "Collecting benchmark corpus seed targets...",
        )
        seed_targets = collect_seed_targets(
            dataset=dataset,
            input_directory=resolved_input_directory,
        )
        total_targets = len(seed_targets)
        emit_progress(
            progress_callback,
            f"Collected {total_targets} document seed target(s).",
        )

        documents: list[RetrievalBenchmarkCorpusDocument] = []
        skipped_targets: list[_CorpusSeedTarget] = []
        for index, seed_target in enumerate(seed_targets, start=1):
            emit_progress(
                progress_callback,
                (
                    f"[{index}/{total_targets}] Starting corpus seed for "
                    f"{seed_target.document_alias} ({seed_target.file_name})"
                ),
            )
            try:
                document = self._seed_target(
                    seed_target,
                    force_reparse_existing=force_reparse_existing,
                    activity_context=activity_context,
                    progress_callback=progress_callback,
                    seed_index=index,
                    total_targets=total_targets,
                )
            except ApplicationError as exc:
                self._rollback()
                skipped_targets.append(seed_target)
                emit_progress(
                    progress_callback,
                    (
                        f"[{index}/{total_targets}] SKIPPED {seed_target.document_alias} "
                        f"({seed_target.file_name}): {exc}. This document was left out of "
                        "the manifest and needs manual intervention (e.g. --force-reparse) "
                        "since the rest of the corpus should not fail because of one "
                        "unrecoverable document."
                    ),
                )
                continue

            documents.append(document)
            emit_progress(
                progress_callback,
                (
                    f"[{index}/{total_targets}] Completed {seed_target.document_alias} "
                    f"-> {document.document_id} "
                    f"(status={document.seed_status}, chunks={document.chunk_count}, "
                    f"questions={document.question_count})"
                ),
            )

        if skipped_targets:
            emit_progress(
                progress_callback,
                (
                    f"{len(skipped_targets)} of {total_targets} document(s) skipped: "
                    + ", ".join(target.document_alias for target in skipped_targets)
                ),
            )

        manifest = RetrievalBenchmarkCorpusManifest(
            truth_set_path=dataset.source_path,
            input_directory=resolved_input_directory,
            generated_at=datetime.now(UTC).isoformat(),
            documents=documents,
        )
        emit_progress(
            progress_callback,
            f"Corpus seeding completed for {manifest.document_count} document(s).",
        )
        return manifest

    def _seed_target(
        self,
        seed_target: _CorpusSeedTarget,
        *,
        force_reparse_existing: bool = False,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
        seed_index: int | None = None,
        total_targets: int | None = None,
    ) -> RetrievalBenchmarkCorpusDocument:
        prefix = progress_prefix(
            index=seed_index,
            total=total_targets,
        )
        emit_progress(
            progress_callback,
            f"{prefix} Computing hashes for {seed_target.file_name}...",
        )
        file_size_bytes = seed_target.file_path.stat().st_size
        file_hash, content_hash = self.hash_computer(seed_target.file_path)
        emit_progress(
            progress_callback,
            f"{prefix} File size: {format_file_size(file_size_bytes)}",
        )

        final_graph, classification, seed_status = resolve_corpus_document(
            seed_target=seed_target,
            file_hash=file_hash,
            force_reparse_existing=force_reparse_existing,
            ingestion_workflow=self.ingestion_workflow,
            duplicate_detection_service=self.duplicate_detection_service,
            document_lookup_service=self.document_lookup_service,
            classification_service=self.classification_service,
            document_classification_workflow=self.document_classification_workflow,
            extraction_service=self.extraction_service,
            unit_of_work=self.unit_of_work,
            activity_context=activity_context,
            progress_callback=progress_callback,
            seed_index=seed_index,
            total_targets=total_targets,
        )

        manifest_content_hash = final_graph.document.hashes.content_hash or content_hash
        return build_manifest_document(
            seed_target=seed_target,
            file_hash=file_hash,
            content_hash=manifest_content_hash,
            document_graph=final_graph,
            classification=classification,
            seed_status=seed_status,
            embedding_model=self.embedding_model,
            vector_collection=self.vector_collection,
        )

    def _rollback(self) -> None:
        if self.unit_of_work is None:
            return
        rollback = getattr(self.unit_of_work, "rollback", None)
        if callable(rollback):
            rollback()
