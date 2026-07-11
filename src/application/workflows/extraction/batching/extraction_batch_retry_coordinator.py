from __future__ import annotations

from collections.abc import Callable

from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.batching.extraction_batch_diagnostics import (
    ExtractionBatchDiagnostics,
)
from src.application.workflows.extraction.batching.extraction_batch_executor import (
    ExtractionBatchExecutor,
)
from src.application.workflows.extraction.batching.extraction_batch_outcome import (
    ExtractionBatchOutcome,
)
from src.application.workflows.extraction.batching.extraction_chunk_batcher import (
    ExtractionChunkBatcher,
)
from src.shared.activity import ActivityContext
from src.shared.exceptions import SchemaValidationError
from src.shared.progress.progress_emitter import emit_progress

# Retries a batch attempt up to `max_attempts` times, then -- if
# `allow_partial_batches` is enabled -- either isolates a multi-chunk
# batch's persistently failing chunks one at a time, or marks a
# single-chunk batch's chunk(s) as unresolved and moves on. Split out of
# extraction_workflow.py's `_extract_batch_with_retries`/
# `_isolate_persistently_failing_batch`.


class ExtractionBatchRetryCoordinator:
    def __init__(
        self,
        *,
        max_attempts: int,
        allow_partial_batches: bool,
        chunk_batcher: ExtractionChunkBatcher,
        batch_executor: ExtractionBatchExecutor,
    ) -> None:
        self.max_attempts = max_attempts
        self.allow_partial_batches = allow_partial_batches
        self.chunk_batcher = chunk_batcher
        self.batch_executor = batch_executor

    def run(
        self,
        *,
        document_id: str,
        batch: ExtractionBatch,
        activity_context: ActivityContext | None,
        progress_callback: Callable[[str], None] | None,
        diagnostics_sink: list[ExtractionBatchDiagnostics],
    ) -> ExtractionBatchOutcome:
        last_exc: SchemaValidationError | None = None
        for attempt_index in range(1, self.max_attempts + 1):
            try:
                return ExtractionBatchOutcome(
                    partial_results=[
                        self.batch_executor.execute_once(
                            document_id=document_id,
                            batch=batch,
                            activity_context=activity_context,
                            progress_callback=progress_callback,
                            previous_error=(
                                self._describe_error_for_feedback(last_exc)
                                if last_exc is not None
                                else None
                            ),
                            diagnostics_sink=diagnostics_sink,
                        )
                    ],
                    attempted_chunk_ids=list(batch.chunk_ids),
                )
            except SchemaValidationError as exc:
                last_exc = exc
                if attempt_index < self.max_attempts:
                    emit_progress(
                        progress_callback,
                        (
                            f"[extraction {batch.batch_index}/{batch.batch_count}] "
                            f"attempt {attempt_index}/{self.max_attempts} failed "
                            f"schema parsing: {exc}. Retrying this batch only..."
                        ),
                    )

        assert last_exc is not None
        if self.allow_partial_batches and len(batch.chunks) > 1:
            return self._isolate_persistently_failing_batch(
                document_id=document_id,
                batch=batch,
                activity_context=activity_context,
                progress_callback=progress_callback,
                diagnostics_sink=diagnostics_sink,
            )

        if self.allow_partial_batches:
            emit_progress(
                progress_callback,
                (
                    f"[extraction {batch.batch_index}/{batch.batch_count}] "
                    f"failed after {self.max_attempts} attempt(s); marking chunk(s) "
                    f"{batch.chunk_ids} as unresolved and continuing with the "
                    "remaining batches."
                ),
            )
            return ExtractionBatchOutcome(
                attempted_chunk_ids=list(batch.chunk_ids),
                unresolved_chunk_ids=list(batch.chunk_ids),
            )

        raise last_exc

    def _isolate_persistently_failing_batch(
        self,
        *,
        document_id: str,
        batch: ExtractionBatch,
        activity_context: ActivityContext | None,
        progress_callback: Callable[[str], None] | None,
        diagnostics_sink: list[ExtractionBatchDiagnostics],
    ) -> ExtractionBatchOutcome:
        single_chunk_batches = self.chunk_batcher.build_single_chunk_batches(batch)
        emit_progress(
            progress_callback,
            (
                f"[extraction {batch.batch_index}/{batch.batch_count}] "
                f"Persistently failing batch contains {len(batch.chunks)} chunk(s). "
                "Retrying each chunk individually to isolate only the failing ones..."
            ),
        )
        outcome = ExtractionBatchOutcome()
        for chunk_index, single_chunk_batch in enumerate(single_chunk_batches, start=1):
            emit_progress(
                progress_callback,
                (
                    f"[extraction {batch.batch_index}/{batch.batch_count}] "
                    f"Isolating chunk {chunk_index}/{len(single_chunk_batches)}: "
                    f"{single_chunk_batch.chunk_ids[0]}"
                ),
            )
            outcome.extend(
                self.run(
                    document_id=document_id,
                    batch=single_chunk_batch,
                    activity_context=activity_context,
                    progress_callback=progress_callback,
                    diagnostics_sink=diagnostics_sink,
                )
            )
        return outcome

    @staticmethod
    def _describe_error_for_feedback(exc: SchemaValidationError) -> str:
        parse_error = exc.details.get("parse_error")
        return parse_error if isinstance(parse_error, str) else str(exc)
