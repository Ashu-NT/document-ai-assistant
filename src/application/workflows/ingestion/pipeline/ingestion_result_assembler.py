from __future__ import annotations

from src.application.workflows.embedding import EmbeddedChunk
from src.application.workflows.ingestion.models.ingestion_request import IngestionRequest
from src.application.workflows.ingestion.models.ingestion_result import IngestionResult
from src.application.workflows.ingestion.models.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.models.ingestion_status import IngestionStatus
from src.domain.workflow import IngestionRun


def build_success_result(
    *,
    request: IngestionRequest,
    ingestion_run: IngestionRun,
    final_graph,
    embedded_chunks: list[EmbeddedChunk],
    file_name: str,
    warnings: list[str],
    correlation_id: str,
    quality_diagnostics: dict[str, object],
    extraction_result,
    extraction_skipped: bool,
    runtime_diagnostics: dict[str, object],
) -> IngestionResult:
    """Assemble the terminal `IngestionResult` for a fully completed run."""
    statistics = final_graph.document.statistics
    diagnostics = {
        "file_path": final_graph.document.file_path,
        "file_hash": final_graph.document.hashes.file_hash,
        "content_hash": final_graph.document.hashes.content_hash,
        "metadata": dict(request.metadata),
        **runtime_diagnostics,
        "quality": quality_diagnostics,
        "extraction_skipped": extraction_skipped,
        "vector_indexing_boundary": (
            "Qdrant writes and SQLite vector mappings are orchestrated in order but are not atomic across both stores."
        ),
    }
    if request.source_name:
        diagnostics["source_name"] = request.source_name
    if extraction_result is not None:
        diagnostics["extraction_id"] = extraction_result.extraction_id
        diagnostics["extraction_unresolved_chunk_count"] = len(
            extraction_result.unresolved_chunk_ids
        )

    return IngestionResult(
        status=IngestionStatus.COMPLETE,
        ingestion_run_id=ingestion_run.run_id,
        document_id=final_graph.document.document_id,
        title=final_graph.document.title,
        file_name=file_name,
        document_type=final_graph.document.document_type.value,
        page_count=statistics.page_count,
        section_count=statistics.section_count,
        element_count=statistics.element_count,
        chunk_count=statistics.chunk_count,
        table_count=statistics.table_count,
        picture_count=statistics.picture_count,
        identifier_count=statistics.identifier_count,
        generated_question_count=len(final_graph.questions),
        vector_count=len(embedded_chunks),
        warnings=warnings,
        diagnostics=diagnostics,
        current_stage=IngestionStage.COMPLETE,
        correlation_id=correlation_id,
    )
