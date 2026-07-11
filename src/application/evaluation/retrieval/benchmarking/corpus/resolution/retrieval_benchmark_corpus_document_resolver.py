from typing import Callable

from src.application.contracts import UnitOfWork
from src.application.evaluation.retrieval.benchmarking.corpus.retrieval_benchmark_seed_target_collector import (
    _CorpusSeedTarget,
)
from src.application.services.classification import ClassificationService
from src.application.services.document import (
    DocumentLookupService,
    DuplicateDetectionService,
)
from src.application.services.extraction import ExtractionService
from src.application.workflows.classification import DocumentClassificationWorkflow
from src.application.workflows.ingestion import IngestionWorkflow
from src.application.workflows.ingestion.ingestion_request import IngestionRequest
from src.domain.classification import DocumentClassification
from src.domain.document import DocumentGraph
from src.shared.activity import ActivityContext
from src.shared.exceptions import ApplicationError
from src.shared.progress.progress_emitter import (
    emit_progress,
    progress_prefix,
    scoped_progress_callback,
)


def resolve_corpus_document(
    *,
    seed_target: _CorpusSeedTarget,
    file_hash: str,
    force_reparse_existing: bool,
    ingestion_workflow: IngestionWorkflow,
    duplicate_detection_service: DuplicateDetectionService,
    document_lookup_service: DocumentLookupService,
    classification_service: ClassificationService,
    document_classification_workflow: DocumentClassificationWorkflow,
    extraction_service: ExtractionService | None,
    unit_of_work: UnitOfWork | None,
    activity_context: ActivityContext | None = None,
    progress_callback: Callable[[str], None] | None = None,
    seed_index: int | None = None,
    total_targets: int | None = None,
) -> tuple[DocumentGraph, DocumentClassification | None, str]:
    """Decide which of the existing-document handling strategies applies to
    `seed_target` (reuse as-is, retry extraction in place, mark as needing a
    full reparse, force-reparse into a new document_id) or, if no duplicate
    exists yet, run the full seed workflow for a genuinely new document.
    """
    prefix = progress_prefix(index=seed_index, total=total_targets)
    emit_progress(
        progress_callback,
        f"{prefix} Checking duplicate status...",
    )
    duplicate_result = duplicate_detection_service.check_file_hash(
        file_hash,
        activity_context=activity_context,
    )
    existing_document_id = duplicate_result.payload.get("existing_document_id")

    if existing_document_id:
        if force_reparse_existing:
            emit_progress(
                progress_callback,
                (
                    f"{prefix} Existing document found for {seed_target.document_alias}: "
                    f"{existing_document_id}. Force reparse enabled; re-ingesting through "
                    "the canonical IngestionWorkflow (this produces a new document_id — "
                    f"{existing_document_id} is left in place, orphaned, since safe "
                    "reingestion-in-place and delete are not yet supported)."
                ),
            )
            final_graph, classification, seed_status = _seed_new_document(
                seed_target=seed_target,
                file_hash=file_hash,
                ingestion_workflow=ingestion_workflow,
                document_lookup_service=document_lookup_service,
                classification_service=classification_service,
                activity_context=activity_context,
                progress_callback=progress_callback,
                seed_index=seed_index,
                total_targets=total_targets,
                resulting_seed_status="reseeded_new",
            )
        elif (
            extraction_service is not None
            and not extraction_service.has_extraction_result(existing_document_id)
        ):
            document_graph = document_lookup_service.get_document_graph(
                existing_document_id,
                activity_context=activity_context,
            )
            if document_graph is None:
                raise ApplicationError(
                    "Existing document could not be loaded to check its chunk count.",
                    details={"document_id": existing_document_id},
                )

            if not document_graph.chunks:
                if not document_graph.elements:
                    emit_progress(
                        progress_callback,
                        (
                            f"{prefix} Existing document found for {seed_target.document_alias}: "
                            f"{existing_document_id}. It has 0 chunks and no persisted elements, "
                            "so in-place recovery is not possible. Marking it as needing a full "
                            "--force-reparse instead of attempting extraction."
                        ),
                    )
                    final_graph, classification, seed_status = (
                        _mark_document_needs_reparse(
                            document_id=existing_document_id,
                            document_graph=document_graph,
                            classification_service=classification_service,
                            activity_context=activity_context,
                        )
                    )
                else:
                    emit_progress(
                        progress_callback,
                        (
                            f"{prefix} Existing document found for {seed_target.document_alias}: "
                            f"{existing_document_id}. It has 0 chunks but "
                            f"{len(document_graph.elements)} persisted element(s). Attempting "
                            "in-place chunk recovery and extraction retry (no re-parse, same "
                            "document_id)..."
                        ),
                    )
                    final_graph, classification, seed_status = (
                        _retry_extraction_for_existing_document(
                            document_id=existing_document_id,
                            ingestion_workflow=ingestion_workflow,
                            document_lookup_service=document_lookup_service,
                            classification_service=classification_service,
                            activity_context=activity_context,
                            progress_callback=progress_callback,
                            seed_index=seed_index,
                            total_targets=total_targets,
                        )
                    )
            else:
                emit_progress(
                    progress_callback,
                    (
                        f"{prefix} Existing document found for {seed_target.document_alias}: "
                        f"{existing_document_id}. It has no extraction result - likely a prior "
                        "run failed mid-batch-extraction. Retrying extraction in place "
                        "(no re-parse, same document_id)..."
                    ),
                )
                final_graph, classification, seed_status = (
                    _retry_extraction_for_existing_document(
                        document_id=existing_document_id,
                        ingestion_workflow=ingestion_workflow,
                        document_lookup_service=document_lookup_service,
                        classification_service=classification_service,
                        activity_context=activity_context,
                        progress_callback=progress_callback,
                        seed_index=seed_index,
                        total_targets=total_targets,
                    )
                )
        elif extraction_service is not None:
            existing_extraction_result = (
                extraction_service.get_document_extraction_result(existing_document_id)
            )
            if (
                existing_extraction_result is not None
                and existing_extraction_result.unresolved_chunk_ids
            ):
                emit_progress(
                    progress_callback,
                    (
                        f"{prefix} Existing document found for {seed_target.document_alias}: "
                        f"{existing_document_id}. Its saved extraction result still has "
                        f"{len(existing_extraction_result.unresolved_chunk_ids)} unresolved "
                        "chunk(s). Retrying only that unresolved subset in place "
                        "(no re-parse, same document_id)..."
                    ),
                )
                final_graph, classification, seed_status = (
                    _retry_extraction_for_existing_document(
                        document_id=existing_document_id,
                        ingestion_workflow=ingestion_workflow,
                        document_lookup_service=document_lookup_service,
                        classification_service=classification_service,
                        activity_context=activity_context,
                        progress_callback=progress_callback,
                        seed_index=seed_index,
                        total_targets=total_targets,
                    )
                )
            else:
                emit_progress(
                    progress_callback,
                    (
                        f"{prefix} Existing document found for {seed_target.document_alias}: "
                        f"{existing_document_id}. Reusing its already-ingested graph as-is."
                    ),
                )
                final_graph, classification, seed_status = _reuse_existing_document(
                    document_id=existing_document_id,
                    document_lookup_service=document_lookup_service,
                    classification_service=classification_service,
                    document_classification_workflow=document_classification_workflow,
                    unit_of_work=unit_of_work,
                    activity_context=activity_context,
                    progress_callback=progress_callback,
                    seed_index=seed_index,
                    total_targets=total_targets,
                )
        else:
            emit_progress(
                progress_callback,
                (
                    f"{prefix} Existing document found for {seed_target.document_alias}: "
                    f"{existing_document_id}. Reusing its already-ingested graph as-is."
                ),
            )
            final_graph, classification, seed_status = _reuse_existing_document(
                document_id=existing_document_id,
                document_lookup_service=document_lookup_service,
                classification_service=classification_service,
                document_classification_workflow=document_classification_workflow,
                unit_of_work=unit_of_work,
                activity_context=activity_context,
                progress_callback=progress_callback,
                seed_index=seed_index,
                total_targets=total_targets,
            )
    else:
        emit_progress(
            progress_callback,
            f"{prefix} No duplicate found. Running full seed workflow...",
        )
        final_graph, classification, seed_status = _seed_new_document(
            seed_target=seed_target,
            file_hash=file_hash,
            ingestion_workflow=ingestion_workflow,
            document_lookup_service=document_lookup_service,
            classification_service=classification_service,
            activity_context=activity_context,
            progress_callback=progress_callback,
            seed_index=seed_index,
            total_targets=total_targets,
        )

    return final_graph, classification, seed_status


def _seed_new_document(
    *,
    seed_target: _CorpusSeedTarget,
    file_hash: str,
    ingestion_workflow: IngestionWorkflow,
    document_lookup_service: DocumentLookupService,
    classification_service: ClassificationService,
    activity_context: ActivityContext | None = None,
    progress_callback: Callable[[str], None] | None = None,
    seed_index: int | None = None,
    total_targets: int | None = None,
    resulting_seed_status: str = "seeded_new",
) -> tuple[DocumentGraph, DocumentClassification | None, str]:
    """Ingest `seed_target` through the canonical `IngestionWorkflow`.

    Used both for genuinely new documents and for `--force-reparse` of an
    already-seeded document. `IngestionRequest` has no way to target an
    existing `document_id` (and reusing one would require re-running
    extraction against it, which is not safe today — extraction results
    are keyed by a fresh `extraction_id` per run with no replace-by-document
    boundary, the same atomicity gap that blocks `IngestionWorkflow.reingest`).
    So a forced reseed always produces a new document_id; the caller passes
    `resulting_seed_status="reseeded_new"` to make that visible in the manifest.
    """
    prefix = progress_prefix(index=seed_index, total=total_targets)
    emit_progress(
        progress_callback,
        f"{prefix} Delegating to canonical IngestionWorkflow...",
    )
    request = IngestionRequest(
        file_path=str(seed_target.file_path),
        force=True,
        requested_by="benchmark_seeder",
        run_quality_checks=False,
    )
    result = ingestion_workflow.run(
        request,
        progress_callback=scoped_progress_callback(progress_callback, prefix),
    )
    final_graph = document_lookup_service.get_document_graph(result.document_id)
    if final_graph is None:
        raise ApplicationError(
            "Seeded document graph could not be loaded after ingestion.",
            details={"document_id": result.document_id},
        )
    classification = classification_service.get_document_classification(result.document_id)
    return final_graph, classification, resulting_seed_status


def _reuse_existing_document(
    *,
    document_id: str,
    document_lookup_service: DocumentLookupService,
    classification_service: ClassificationService,
    document_classification_workflow: DocumentClassificationWorkflow,
    unit_of_work: UnitOfWork | None,
    activity_context: ActivityContext | None = None,
    progress_callback: Callable[[str], None] | None = None,
    seed_index: int | None = None,
    total_targets: int | None = None,
) -> tuple[DocumentGraph, DocumentClassification | None, str]:
    """Reuse an already-ingested document as-is, without reparsing or
    re-finalizing anything.

    This is safe (and correct, not just cheap) because the caller
    (`resolve_corpus_document`) only reaches this method after confirming the
    document has a completed extraction result — a document whose
    extraction never finished (e.g. a prior run failed mid-batch) is
    routed to `_retry_extraction_for_existing_document` instead. So
    chunks, embeddings, extraction, and identifiers are already
    complete and consistent here; re-running finalization would only
    redo work with the same file content, for no benefit.
    """
    prefix = progress_prefix(index=seed_index, total=total_targets)
    emit_progress(
        progress_callback,
        f"{prefix} Loading existing persisted document graph...",
    )
    document_graph = document_lookup_service.get_document_graph(
        document_id,
        activity_context=activity_context,
    )
    if document_graph is None:
        raise ApplicationError(
            "Existing seeded document could not be loaded.",
            details={"document_id": document_id},
        )

    classification = classification_service.get_document_classification(document_id)
    if classification is None:
        emit_progress(
            progress_callback,
            f"{prefix} Existing classification missing. Reclassifying document...",
        )
        classification = document_classification_workflow.classify_document(
            document_graph,
            activity_context=activity_context,
        )
        _commit(unit_of_work)
    else:
        emit_progress(
            progress_callback,
            f"{prefix} Reusing existing document classification.",
        )

    return document_graph, classification, "reused_existing"


def _retry_extraction_for_existing_document(
    *,
    document_id: str,
    ingestion_workflow: IngestionWorkflow,
    document_lookup_service: DocumentLookupService,
    classification_service: ClassificationService,
    activity_context: ActivityContext | None = None,
    progress_callback: Callable[[str], None] | None = None,
    seed_index: int | None = None,
    total_targets: int | None = None,
) -> tuple[DocumentGraph, DocumentClassification | None, str]:
    """Repair a document whose extraction never completed (its
    `documents`/`chunks`/`sections` rows were already committed by a
    prior run before that run's extraction step raised), by retrying
    only extraction — and, if enabled, semantic linking — through
    `IngestionWorkflow.retry_extraction`. Does not re-parse the source
    file or mint a new document_id.
    """
    prefix = progress_prefix(index=seed_index, total=total_targets)
    emit_progress(
        progress_callback,
        f"{prefix} Retrying extraction for {document_id}...",
    )
    ingestion_workflow.retry_extraction(
        document_id,
        activity_context=activity_context,
        progress_callback=scoped_progress_callback(progress_callback, prefix),
    )

    document_graph = document_lookup_service.get_document_graph(
        document_id,
        activity_context=activity_context,
    )
    if document_graph is None:
        raise ApplicationError(
            "Document could not be reloaded after retrying extraction.",
            details={"document_id": document_id},
        )

    classification = classification_service.get_document_classification(document_id)
    return document_graph, classification, "extraction_retried"


def _mark_document_needs_reparse(
    *,
    document_id: str,
    document_graph: DocumentGraph,
    classification_service: ClassificationService,
    activity_context: ActivityContext | None = None,
) -> tuple[DocumentGraph, DocumentClassification | None, str]:
    """A document with zero chunks has nothing for extraction to run
    against *and* no persisted elements to rebuild from — it failed before
    a usable graph was committed, so only a full `--force-reparse` can fix
    it. Rather than raising and dropping the
    document out of the manifest entirely, it is included as-is
    (`chunk_count=0`) with a distinguishing `seed_status` so it stays
    visible and actionable instead of silently disappearing.
    """
    classification = classification_service.get_document_classification(document_id)
    return document_graph, classification, "no_chunks_needs_reparse"


def _commit(unit_of_work: UnitOfWork | None) -> None:
    if unit_of_work is None:
        return
    unit_of_work.commit()
