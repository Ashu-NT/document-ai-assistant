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
from src.application.workflows.extraction.candidates.extraction_candidate_routing_diagnostics import (
    ExtractionCandidateRoutingDiagnostics,
)
from src.application.workflows.extraction.execution_budget import (
    ExtractionExecutionBudget,
    describe_budget_exhaustion,
)
from src.shared.activity import ActivityContext
from src.shared.exceptions import LLMProviderError, SchemaValidationError
from src.shared.progress.progress_emitter import emit_progress


_RETRYABLE_EXCEPTIONS = (SchemaValidationError, LLMProviderError)


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
        candidate_routing_diagnostics_sink: (
            list[ExtractionCandidateRoutingDiagnostics] | None
        ) = None,
        budget: ExtractionExecutionBudget | None = None,
    ) -> ExtractionBatchOutcome:
        last_exc: SchemaValidationError | LLMProviderError | None = None
        for attempt_index in range(1, self.max_attempts + 1):
            if budget is not None and budget.is_expired():
                last_exc = self._budget_exhausted_error(batch)
                diagnostics_sink.append(
                    ExtractionBatchDiagnostics(
                        batch_index=batch.batch_index,
                        batch_count=batch.batch_count,
                        chunk_ids=batch.chunk_ids,
                        char_count=batch.char_count,
                        word_count=batch.word_count,
                        model_name=self.batch_executor.extraction_model,
                        parse_success=False,
                        parse_error=str(last_exc),
                        budget_exhausted=True,
                    )
                )
                emit_progress(
                    progress_callback,
                    (
                        f"[extraction {batch.batch_index}/{batch.batch_count}] "
                        f"{describe_budget_exhaustion(budget)}; no further "
                        "extraction attempts will be scheduled for this batch."
                    ),
                )
                break
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
                            candidate_routing_diagnostics_sink=candidate_routing_diagnostics_sink,
                        )
                    ],
                    attempted_chunk_ids=list(batch.chunk_ids),
                )
            except _RETRYABLE_EXCEPTIONS as exc:
                last_exc = exc
                failure_label = (
                    "schema parsing"
                    if isinstance(exc, SchemaValidationError)
                    else f"LLM call ({exc.details.get('failure_kind', 'unknown')})"
                )
                if attempt_index < self.max_attempts:
                    emit_progress(
                        progress_callback,
                        (
                            f"[extraction {batch.batch_index}/{batch.batch_count}] "
                            f"attempt {attempt_index}/{self.max_attempts} failed "
                            f"{failure_label}: {exc}. Retrying this batch only..."
                        ),
                    )

        assert last_exc is not None
        budget_expired = budget is not None and budget.is_expired()
        if self.allow_partial_batches and len(batch.chunks) > 1 and not budget_expired:
            return self._isolate_persistently_failing_batch(
                document_id=document_id,
                batch=batch,
                activity_context=activity_context,
                progress_callback=progress_callback,
                diagnostics_sink=diagnostics_sink,
                candidate_routing_diagnostics_sink=candidate_routing_diagnostics_sink,
                budget=budget,
            )

        if self.allow_partial_batches:
            reason = (
                describe_budget_exhaustion(budget)
                if budget_expired and budget is not None
                else f"failed after {self.max_attempts} attempt(s)"
            )
            emit_progress(
                progress_callback,
                (
                    f"[extraction {batch.batch_index}/{batch.batch_count}] "
                    f"{reason}; marking chunk(s) {batch.chunk_ids} as unresolved "
                    "and continuing with the remaining batches."
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
        candidate_routing_diagnostics_sink: (
            list[ExtractionCandidateRoutingDiagnostics] | None
        ) = None,
        budget: ExtractionExecutionBudget | None = None,
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
                    candidate_routing_diagnostics_sink=candidate_routing_diagnostics_sink,
                    budget=budget,
                )
            )
        return outcome

    @staticmethod
    def _describe_error_for_feedback(
        exc: SchemaValidationError | LLMProviderError,
    ) -> str:
        parse_error = exc.details.get("parse_error")
        return parse_error if isinstance(parse_error, str) else str(exc)

    @staticmethod
    def _budget_exhausted_error(batch: ExtractionBatch) -> LLMProviderError:
        return LLMProviderError(
            "Execution budget exhausted before this batch could be attempted.",
            details={
                "failure_kind": "budget_exhausted",
                "batch_index": batch.batch_index,
                "batch_count": batch.batch_count,
                "chunk_ids": batch.chunk_ids,
            },
        )
