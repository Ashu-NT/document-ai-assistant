import hashlib
from time import perf_counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from src.application.contracts import UnitOfWork
from src.application.evaluation.retrieval.benchmarking.corpus.models import (
    RetrievalBenchmarkCorpusDocument,
    RetrievalBenchmarkCorpusManifest,
)
from src.application.evaluation.retrieval.benchmarking.datasets import (
    RetrievalBenchmarkDataset,
)
from src.application.evaluation.retrieval.benchmarking.loaders import (
    RetrievalTruthSetLoader,
)
from src.application.services.classification import ClassificationService
from src.application.services.document import (
    DocumentLookupService,
    DocumentRegistrationService,
    DuplicateDetectionService,
)
from src.application.workflows.classification import (
    DocumentClassificationWorkflow,
    PostClassificationChunkFinalizationWorkflow,
)
from src.application.workflows.parsing import ParsingWorkflow
from src.domain.classification import DocumentClassification
from src.domain.document import DocumentGraph
from src.shared.activity import ActivityContext
from src.shared.exceptions import ApplicationError, SchemaValidationError


@dataclass(slots=True)
class _CorpusSeedTarget:
    document_alias: str
    file_name: str
    file_path: Path


class RetrievalBenchmarkCorpusSeeder:
    def __init__(
        self,
        *,
        parsing_workflow: ParsingWorkflow,
        document_registration_service: DocumentRegistrationService,
        duplicate_detection_service: DuplicateDetectionService,
        document_lookup_service: DocumentLookupService,
        classification_service: ClassificationService,
        document_classification_workflow: DocumentClassificationWorkflow,
        post_classification_chunk_finalization_workflow: (
            PostClassificationChunkFinalizationWorkflow
        ),
        truth_set_loader: RetrievalTruthSetLoader | None = None,
        unit_of_work: UnitOfWork | None = None,
        embedding_model: str | None = None,
        vector_collection: str | None = None,
        hash_computer: Callable[[Path], tuple[str, str | None]] | None = None,
    ) -> None:
        self.parsing_workflow = parsing_workflow
        self.document_registration_service = document_registration_service
        self.duplicate_detection_service = duplicate_detection_service
        self.document_lookup_service = document_lookup_service
        self.classification_service = classification_service
        self.document_classification_workflow = document_classification_workflow
        self.post_classification_chunk_finalization_workflow = (
            post_classification_chunk_finalization_workflow
        )
        self.truth_set_loader = truth_set_loader or RetrievalTruthSetLoader()
        self.unit_of_work = unit_of_work
        self.embedding_model = embedding_model
        self.vector_collection = vector_collection
        self.hash_computer = hash_computer or self._compute_hashes

    def seed_corpus(
        self,
        *,
        truth_set_path: Path | str | None = None,
        input_directory: Path | str | None = None,
        force_reparse_existing: bool = False,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> RetrievalBenchmarkCorpusManifest:
        self._emit_progress(
            progress_callback,
            "Loading retrieval benchmark truth set...",
        )
        dataset = self.truth_set_loader.load(truth_set_path)
        resolved_input_directory = self._resolve_input_directory(
            input_directory=input_directory,
            dataset=dataset,
        )
        self._emit_progress(
            progress_callback,
            f"Using input directory: {resolved_input_directory}",
        )
        self._emit_progress(
            progress_callback,
            "Collecting benchmark corpus seed targets...",
        )
        seed_targets = self._collect_seed_targets(
            dataset=dataset,
            input_directory=resolved_input_directory,
        )
        total_targets = len(seed_targets)
        self._emit_progress(
            progress_callback,
            f"Collected {total_targets} document seed target(s).",
        )

        documents: list[RetrievalBenchmarkCorpusDocument] = []
        for index, seed_target in enumerate(seed_targets, start=1):
            self._emit_progress(
                progress_callback,
                (
                    f"[{index}/{total_targets}] Starting corpus seed for "
                    f"{seed_target.document_alias} ({seed_target.file_name})"
                ),
            )
            document = self._seed_target(
                seed_target,
                force_reparse_existing=force_reparse_existing,
                activity_context=activity_context,
                progress_callback=progress_callback,
                seed_index=index,
                total_targets=total_targets,
            )
            documents.append(document)
            self._emit_progress(
                progress_callback,
                (
                    f"[{index}/{total_targets}] Completed {seed_target.document_alias} "
                    f"-> {document.document_id} "
                    f"(status={document.seed_status}, chunks={document.chunk_count}, "
                    f"questions={document.question_count})"
                ),
            )

        manifest = RetrievalBenchmarkCorpusManifest(
            truth_set_path=dataset.source_path,
            input_directory=resolved_input_directory,
            generated_at=datetime.now(UTC).isoformat(),
            documents=documents,
        )
        self._emit_progress(
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
        prefix = self._progress_prefix(
            seed_index=seed_index,
            total_targets=total_targets,
        )
        self._emit_progress(
            progress_callback,
            f"{prefix} Computing hashes for {seed_target.file_name}...",
        )
        file_size_bytes = seed_target.file_path.stat().st_size
        file_hash, content_hash = self.hash_computer(seed_target.file_path)
        self._emit_progress(
            progress_callback,
            f"{prefix} File size: {self._format_file_size(file_size_bytes)}",
        )
        self._emit_progress(
            progress_callback,
            f"{prefix} Checking duplicate status...",
        )
        duplicate_result = self.duplicate_detection_service.check_file_hash(
            file_hash,
            activity_context=activity_context,
        )
        existing_document_id = duplicate_result.payload.get("existing_document_id")

        if existing_document_id:
            if force_reparse_existing:
                self._emit_progress(
                    progress_callback,
                    (
                        f"{prefix} Existing document found for {seed_target.document_alias}: "
                        f"{existing_document_id}. Force reparse enabled; rebuilding persisted document graph."
                    ),
                )
                final_graph, classification, seed_status = (
                    self._reseed_existing_document(
                        document_id=existing_document_id,
                        seed_target=seed_target,
                        file_hash=file_hash,
                        content_hash=content_hash,
                        activity_context=activity_context,
                        progress_callback=progress_callback,
                        seed_index=seed_index,
                        total_targets=total_targets,
                    )
                )
            else:
                self._emit_progress(
                    progress_callback,
                    (
                        f"{prefix} Existing document found for {seed_target.document_alias}: "
                        f"{existing_document_id}"
                    ),
                )
                final_graph, classification, seed_status = self._refresh_existing_document(
                    document_id=existing_document_id,
                    activity_context=activity_context,
                    progress_callback=progress_callback,
                    seed_index=seed_index,
                    total_targets=total_targets,
                )
        else:
            self._emit_progress(
                progress_callback,
                f"{prefix} No duplicate found. Running full seed workflow...",
            )
            final_graph, classification, seed_status = self._seed_new_document(
                seed_target=seed_target,
                file_hash=file_hash,
                content_hash=content_hash,
                activity_context=activity_context,
                progress_callback=progress_callback,
                seed_index=seed_index,
                total_targets=total_targets,
            )

        return self._build_manifest_document(
            seed_target=seed_target,
            file_hash=file_hash,
            content_hash=content_hash,
            document_graph=final_graph,
            classification=classification,
            seed_status=seed_status,
        )

    def _seed_new_document(
        self,
        *,
        seed_target: _CorpusSeedTarget,
        file_hash: str,
        content_hash: str | None,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
        seed_index: int | None = None,
        total_targets: int | None = None,
    ) -> tuple[DocumentGraph, DocumentClassification | None, str]:
        prefix = self._progress_prefix(
            seed_index=seed_index,
            total_targets=total_targets,
        )
        self._emit_progress(
            progress_callback,
            f"{prefix} Parsing document into provisional graph...",
        )
        parsing_progress = self._scoped_progress_callback(
            progress_callback,
            prefix,
        )
        parsing_started_at = perf_counter()
        parsing_result = self.parsing_workflow.parse(
            file_path=str(seed_target.file_path),
            file_hash=file_hash,
            content_hash=content_hash,
            activity_context=activity_context,
            progress_callback=parsing_progress,
        )
        parsing_elapsed_seconds = perf_counter() - parsing_started_at
        self._emit_progress(
            progress_callback,
            (
                f"{prefix} Provisional parsing completed in "
                f"{self._format_elapsed_seconds(parsing_elapsed_seconds)}. "
                "Registering provisional document graph "
                f"({len(parsing_result.document_graph.chunks)} chunk(s))."
            ),
        )
        self.document_registration_service.register_document_graph(
            parsing_result.document_graph,
            activity_context=activity_context,
        )
        self._commit()

        self._emit_progress(
            progress_callback,
            f"{prefix} Running document classification...",
        )
        classification = self.document_classification_workflow.classify_document(
            parsing_result.document_graph,
            activity_context=activity_context,
        )
        self._commit()

        self._emit_progress(
            progress_callback,
            (
                f"{prefix} Finalizing post-classification chunks, questions, "
                "and embeddings..."
            ),
        )
        final_graph = self.post_classification_chunk_finalization_workflow.finalize(
            parsing_result.document_id,
            activity_context=activity_context,
            progress_callback=self._scoped_progress_callback(
                progress_callback,
                prefix,
            ),
        )
        self._commit()

        return final_graph, classification, "seeded_new"

    def _reseed_existing_document(
        self,
        *,
        document_id: str,
        seed_target: _CorpusSeedTarget,
        file_hash: str,
        content_hash: str | None,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
        seed_index: int | None = None,
        total_targets: int | None = None,
    ) -> tuple[DocumentGraph, DocumentClassification | None, str]:
        prefix = self._progress_prefix(
            seed_index=seed_index,
            total_targets=total_targets,
        )
        self._emit_progress(
            progress_callback,
            f"{prefix} Reparsing document with the existing document ID...",
        )
        parsing_progress = self._scoped_progress_callback(
            progress_callback,
            prefix,
        )
        parsing_started_at = perf_counter()
        parsing_result = self.parsing_workflow.parse(
            file_path=str(seed_target.file_path),
            file_hash=file_hash,
            content_hash=content_hash,
            document_id=document_id,
            activity_context=activity_context,
            progress_callback=parsing_progress,
        )
        parsing_elapsed_seconds = perf_counter() - parsing_started_at
        self._emit_progress(
            progress_callback,
            (
                f"{prefix} Reparse completed in "
                f"{self._format_elapsed_seconds(parsing_elapsed_seconds)}. "
                "Replacing persisted document graph "
                f"({len(parsing_result.document_graph.chunks)} chunk(s))."
            ),
        )
        self.document_registration_service.replace_document_graph(
            parsing_result.document_graph,
            activity_context=activity_context,
        )
        self._commit()

        self._emit_progress(
            progress_callback,
            f"{prefix} Re-running document classification on rebuilt graph...",
        )
        classification = self.document_classification_workflow.classify_document(
            parsing_result.document_graph,
            activity_context=activity_context,
        )
        self._commit()

        self._emit_progress(
            progress_callback,
            (
                f"{prefix} Finalizing post-classification chunks, questions, "
                "and embeddings for rebuilt document..."
            ),
        )
        final_graph = self.post_classification_chunk_finalization_workflow.finalize(
            document_id,
            activity_context=activity_context,
            progress_callback=self._scoped_progress_callback(
                progress_callback,
                prefix,
            ),
        )
        self._commit()

        return final_graph, classification, "reseeded_existing"

    def _refresh_existing_document(
        self,
        *,
        document_id: str,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
        seed_index: int | None = None,
        total_targets: int | None = None,
    ) -> tuple[DocumentGraph, DocumentClassification | None, str]:
        prefix = self._progress_prefix(
            seed_index=seed_index,
            total_targets=total_targets,
        )
        self._emit_progress(
            progress_callback,
            f"{prefix} Loading existing persisted document graph...",
        )
        document_graph = self.document_lookup_service.get_document_graph(
            document_id,
            activity_context=activity_context,
        )
        if document_graph is None:
            raise ApplicationError(
                "Existing seeded document could not be loaded.",
                details={"document_id": document_id},
            )

        classification = self.classification_service.get_document_classification(
            document_id
        )
        if classification is None:
            self._emit_progress(
                progress_callback,
                f"{prefix} Existing classification missing. Reclassifying document...",
            )
            classification = self.document_classification_workflow.classify_document(
                document_graph,
                activity_context=activity_context,
            )
            self._commit()
        else:
            self._emit_progress(
                progress_callback,
                f"{prefix} Reusing existing document classification.",
            )

        self._emit_progress(
            progress_callback,
            (
                f"{prefix} Re-finalizing chunks, questions, and embeddings for "
                "existing document..."
            ),
        )
        final_graph = self.post_classification_chunk_finalization_workflow.finalize(
            document_id,
            activity_context=activity_context,
            progress_callback=self._scoped_progress_callback(
                progress_callback,
                prefix,
            ),
        )
        self._commit()

        refreshed_classification = (
            self.classification_service.get_document_classification(document_id)
            or classification
        )
        return final_graph, refreshed_classification, "refinalized_existing"

    def _build_manifest_document(
        self,
        *,
        seed_target: _CorpusSeedTarget,
        file_hash: str,
        content_hash: str | None,
        document_graph: DocumentGraph,
        classification: DocumentClassification | None,
        seed_status: str,
    ) -> RetrievalBenchmarkCorpusDocument:
        result = classification.result if classification is not None else None
        return RetrievalBenchmarkCorpusDocument(
            document_alias=seed_target.document_alias,
            document_id=document_graph.document.document_id,
            file_name=seed_target.file_name,
            file_path=seed_target.file_path,
            file_hash=file_hash,
            content_hash=content_hash,
            document_type=document_graph.document.document_type.value,
            page_count=document_graph.document.statistics.page_count,
            section_count=len(document_graph.sections),
            element_count=len(document_graph.elements),
            chunk_count=len(document_graph.chunks),
            question_count=len(document_graph.questions),
            classification_label=(
                classification.document_type.value
                if classification is not None
                else None
            ),
            classification_confidence=(
                result.confidence_score
                if result is not None
                else None
            ),
            embedding_model=self.embedding_model,
            vector_collection=self.vector_collection,
            seed_status=seed_status,
        )

    def _collect_seed_targets(
        self,
        *,
        dataset: RetrievalBenchmarkDataset,
        input_directory: Path,
    ) -> list[_CorpusSeedTarget]:
        file_by_alias: dict[str, str] = {}
        alias_by_file: dict[str, str] = {}
        ordered_targets: list[_CorpusSeedTarget] = []

        for case in dataset.canonical_cases:
            alias = case.expected_document_alias
            file_name = case.expected_file_name

            if not alias or not file_name:
                raise SchemaValidationError(
                    "Retrieval benchmark case is missing document alias or file name.",
                    details={
                        "case_id": case.case_id,
                    },
                )

            existing_file_name = file_by_alias.get(alias)
            if existing_file_name is not None and existing_file_name != file_name:
                raise SchemaValidationError(
                    "Retrieval benchmark dataset maps one alias to multiple files.",
                    details={
                        "document_alias": alias,
                        "first_file_name": existing_file_name,
                        "conflicting_file_name": file_name,
                    },
                )

            existing_alias = alias_by_file.get(file_name)
            if existing_alias is not None and existing_alias != alias:
                raise SchemaValidationError(
                    "Retrieval benchmark dataset maps one file to multiple aliases.",
                    details={
                        "file_name": file_name,
                        "first_alias": existing_alias,
                        "conflicting_alias": alias,
                    },
                )

            if alias in file_by_alias:
                continue

            file_path = input_directory / file_name
            if not file_path.exists() or not file_path.is_file():
                raise SchemaValidationError(
                    "Retrieval benchmark corpus file not found.",
                    details={
                        "document_alias": alias,
                        "file_name": file_name,
                        "input_directory": str(input_directory),
                    },
                )

            file_by_alias[alias] = file_name
            alias_by_file[file_name] = alias
            ordered_targets.append(
                _CorpusSeedTarget(
                    document_alias=alias,
                    file_name=file_name,
                    file_path=file_path,
                )
            )

        return ordered_targets

    @staticmethod
    def _resolve_input_directory(
        *,
        input_directory: Path | str | None,
        dataset: RetrievalBenchmarkDataset,
    ) -> Path:
        if input_directory is None:
            return dataset.source_path.parent
        return Path(input_directory)

    @staticmethod
    def _compute_hashes(file_path: Path) -> tuple[str, str]:
        digest = hashlib.sha256()

        with file_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)

        file_hash = digest.hexdigest()
        return file_hash, file_hash

    @staticmethod
    def _format_file_size(file_size_bytes: int) -> str:
        if file_size_bytes < 1024:
            return f"{file_size_bytes} B"

        suffixes = ["KB", "MB", "GB", "TB"]
        size = float(file_size_bytes)
        suffix_index = -1
        while size >= 1024 and suffix_index < len(suffixes) - 1:
            size /= 1024
            suffix_index += 1

        precision = 0 if size >= 100 else 1
        return f"{size:.{precision}f} {suffixes[max(suffix_index, 0)]}"

    @staticmethod
    def _format_elapsed_seconds(elapsed_seconds: float) -> str:
        if elapsed_seconds < 1:
            return f"{elapsed_seconds:.2f}s"
        if elapsed_seconds < 60:
            return f"{elapsed_seconds:.1f}s"

        minutes, seconds = divmod(elapsed_seconds, 60.0)
        if minutes < 60:
            return f"{int(minutes)}m {seconds:.1f}s"

        hours, minutes = divmod(minutes, 60.0)
        return f"{int(hours)}h {int(minutes)}m {seconds:.1f}s"

    def _commit(self) -> None:
        if self.unit_of_work is None:
            return
        self.unit_of_work.commit()

    @staticmethod
    def _emit_progress(
        progress_callback: Callable[[str], None] | None,
        message: str,
    ) -> None:
        if progress_callback is not None:
            progress_callback(message)

    @staticmethod
    def _progress_prefix(
        *,
        seed_index: int | None,
        total_targets: int | None,
    ) -> str:
        if seed_index is None or total_targets is None:
            return "[seed]"
        return f"[{seed_index}/{total_targets}]"

    @classmethod
    def _scoped_progress_callback(
        cls,
        progress_callback: Callable[[str], None] | None,
        prefix: str,
    ) -> Callable[[str], None] | None:
        if progress_callback is None:
            return None

        def scoped_callback(message: str) -> None:
            cls._emit_progress(progress_callback, f"{prefix} {message}")

        return scoped_callback
