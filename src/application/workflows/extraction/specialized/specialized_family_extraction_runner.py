from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field, replace as dataclass_replace

from src.application.services.ai import LLMService
from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.batching.extraction_batch_diagnostics import (
    ExtractionBatchDiagnostics,
)
from src.application.workflows.extraction.batching.extraction_batch_retry_coordinator import (
    ExtractionBatchRetryCoordinator,
)
from src.application.workflows.extraction.batching.extraction_chunk_batcher import (
    ExtractionChunkBatcher,
)
from src.application.workflows.extraction.candidates.extraction_candidate_routing_diagnostics import (
    ExtractionCandidateRoutingDiagnostics,
)
from src.application.workflows.extraction.candidates.extraction_candidate_selector import (
    ExtractionCandidateSelector,
)
from src.application.workflows.extraction.execution_budget import (
    ExtractionExecutionBudget,
    describe_budget_exhaustion,
)
from src.application.workflows.extraction.extraction_execution_strategy import (
    ExtractionExecutionStrategy,
)
from src.application.workflows.extraction.extraction_result_assembler import (
    ExtractionResultAssembler,
)
from src.application.prompts.extraction.common.extraction_prompt_type import (
    ExtractionPromptType,
)
from src.application.workflows.extraction.specialized.extraction_plan import (
    ExtractionWorkItem,
    build_extraction_plan,
)
from src.application.workflows.extraction.specialized.maintenance_task_component_backfill import (
    backfill_maintenance_task_component_names,
)
from src.application.workflows.extraction.specialized.specialized_extraction_batch_executor import (
    SpecializedExtractionBatchExecutor,
)
from src.application.workflows.extraction.table_windowing import (
    TableEvidenceWindow,
    TableEvidenceWindowBuilder,
    TableWindowActivationPolicy,
    resolve_composed_table,
)
from src.domain.assets import TableAsset
from src.domain.extraction import ExtractionResult, UnresolvedExtractionWork
from src.shared.activity import ActivityContext
from src.shared.progress.progress_emitter import emit_progress

_BUDGET_EXHAUSTED_ENTITY_TYPE = "budget_exhausted"

# Top-level SPECIALIZED_FAMILY composition: given the SAME batches
# ExtractionChunkBatcher already built for MULTI_FAMILY, expands them into an
# ExtractionPlan (one work item per (batch, family) pair) and runs each work
# item through its OWN independent ExtractionBatchRetryCoordinator instance,
# bound to a SpecializedExtractionBatchExecutor for that one family.
#
# Reusing the existing, unmodified ExtractionBatchRetryCoordinator once per
# family -- rather than writing new cross-family retry/failure-isolation
# logic -- is what makes "a failure in one entity family must not erase
# successful extraction from another family" true by construction: each
# family's retry/split lifecycle is a fully independent invocation of the
# same proven coordinator, so one family's exhausted retries/unresolved
# chunks can never affect another family's already-collected partial_results.
#
# PHASE 2B MAINTENANCE TABLE ROW-WINDOW EXTRACTION EXPERIMENT: when
# `table_window_activation_policy` says a work item's single-chunk batch is
# a large structured table for an activated family, THIS SAME per-work-item
# loop additionally fans that one work item out into one independent
# ExtractionBatchRetryCoordinator run PER ROW WINDOW, instead of one call
# covering the whole table. The ExtractionPlan itself (candidate-family
# selection, batching) is completely unchanged; only how ONE work item's
# evidence is presented at execution time differs.


@dataclass(slots=True)
class SpecializedFamilyExtractionRunResult:
    partial_results: list[ExtractionResult] = field(default_factory=list)
    attempted_chunk_ids: list[str] = field(default_factory=list)
    unresolved_chunk_ids: list[str] = field(default_factory=list)
    unresolved_extraction_work: list[UnresolvedExtractionWork] = field(
        default_factory=list
    )


class SpecializedFamilyExtractionRunner:
    def __init__(
        self,
        *,
        llm_service: LLMService,
        extraction_model: str | None,
        temperature: float,
        json_mode: bool,
        failure_preview_chars: int,
        max_attempts: int,
        allow_partial_batches: bool,
        chunk_batcher: ExtractionChunkBatcher,
        candidate_selector: ExtractionCandidateSelector,
        result_assembler: ExtractionResultAssembler,
        table_window_activation_policy: TableWindowActivationPolicy | None = None,
        table_window_builder: TableEvidenceWindowBuilder | None = None,
        num_predict: int | None = None,
        num_ctx: int | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.extraction_model = extraction_model
        self.temperature = temperature
        self.json_mode = json_mode
        self.failure_preview_chars = failure_preview_chars
        self.max_attempts = max_attempts
        self.allow_partial_batches = allow_partial_batches
        self.chunk_batcher = chunk_batcher
        self.candidate_selector = candidate_selector
        self.result_assembler = result_assembler
        self.num_predict = num_predict
        self.num_ctx = num_ctx
        self.table_window_activation_policy = (
            table_window_activation_policy
            or TableWindowActivationPolicy(enabled=False, rows_per_window=10)
        )
        self.table_window_builder = table_window_builder or TableEvidenceWindowBuilder(
            rows_per_window=self.table_window_activation_policy.rows_per_window
        )

    def run(
        self,
        *,
        document_id: str,
        batches: list[ExtractionBatch],
        activity_context: ActivityContext | None,
        progress_callback: Callable[[str], None] | None,
        diagnostics_sink: list[ExtractionBatchDiagnostics],
        tables: dict[str, TableAsset] | None = None,
        candidate_routing_diagnostics_sink: (
            list[ExtractionCandidateRoutingDiagnostics] | None
        ) = None,
        budget: ExtractionExecutionBudget | None = None,
    ) -> SpecializedFamilyExtractionRunResult:
        result = SpecializedFamilyExtractionRunResult()
        for batch in batches:
            if budget is not None and budget.is_expired():
                emit_progress(
                    progress_callback,
                    (
                        f"[extraction {batch.batch_index}/{batch.batch_count}] "
                        f"{describe_budget_exhaustion(budget)}; skipping "
                        "candidate-family selection and marking chunk(s) "
                        f"{batch.chunk_ids} as unresolved."
                    ),
                )
                result.unresolved_chunk_ids.extend(batch.chunk_ids)
                result.unresolved_extraction_work.extend(
                    UnresolvedExtractionWork(
                        chunk_id=chunk_id, entity_type=_BUDGET_EXHAUSTED_ENTITY_TYPE
                    )
                    for chunk_id in batch.chunk_ids
                )
                continue

            plan = build_extraction_plan(
                [batch],
                candidate_selector=self.candidate_selector,
                document_id=document_id,
                candidate_routing_diagnostics_sink=candidate_routing_diagnostics_sink,
            )
            for work_item in plan.work_items:
                resolved = self._resolve_windows(work_item, tables=tables or {})
                if resolved is None:
                    self._run_single_work_item(
                        document_id=document_id,
                        work_item=work_item,
                        activity_context=activity_context,
                        progress_callback=progress_callback,
                        diagnostics_sink=diagnostics_sink,
                        result=result,
                        budget=budget,
                        tables=tables,
                    )
                else:
                    windows, composed_table = resolved
                    self._run_windowed_work_item(
                        document_id=document_id,
                        work_item=work_item,
                        windows=windows,
                        composed_table=composed_table,
                        activity_context=activity_context,
                        progress_callback=progress_callback,
                        diagnostics_sink=diagnostics_sink,
                        result=result,
                        budget=budget,
                        tables=tables,
                    )

        return result

    def _resolve_windows(
        self,
        work_item: ExtractionWorkItem,
        *,
        tables: dict[str, TableAsset],
    ) -> tuple[list[TableEvidenceWindow], TableAsset] | None:
        """Returns the row windows to use for this work item (plus the
        composed canonical table they were built from), or None when
        windowing does not apply (the normal, unwindowed path runs
        instead). Deliberately conservative: only a batch consisting of
        EXACTLY ONE table-bearing chunk is considered - a mixed batch (the
        table chunk alongside unrelated chunks) falls back to the existing
        unwindowed behavior rather than inventing a multi-chunk windowing
        scheme this experiment does not need."""
        chunks = work_item.batch.chunks
        if len(chunks) != 1:
            return None

        chunk = chunks[0]
        if not chunk.table_ids:
            return None

        composed_table = resolve_composed_table(chunk, tables)
        if composed_table is None:
            return None

        if not self.table_window_activation_policy.should_window(
            entity_type=work_item.entity_type,
            execution_strategy=ExtractionExecutionStrategy.SPECIALIZED_FAMILY,
            table=composed_table,
        ):
            return None

        windows = self.table_window_builder.build_windows(
            composed_table, source_chunk_id=chunk.chunk_id
        )
        if not windows:
            return None
        return windows, composed_table

    def _run_single_work_item(
        self,
        *,
        document_id: str,
        work_item: ExtractionWorkItem,
        activity_context: ActivityContext | None,
        progress_callback: Callable[[str], None] | None,
        diagnostics_sink: list[ExtractionBatchDiagnostics],
        result: SpecializedFamilyExtractionRunResult,
        budget: ExtractionExecutionBudget | None = None,
        tables: dict[str, TableAsset] | None = None,
    ) -> None:
        if budget is not None and budget.is_expired():
            emit_progress(
                progress_callback,
                (
                    f"[extraction {work_item.batch.batch_index}/"
                    f"{work_item.batch.batch_count}] "
                    f"[specialized:{work_item.entity_type.value}] "
                    f"{describe_budget_exhaustion(budget)}; skipping this "
                    "family's extraction call."
                ),
            )
        coordinator = self._build_coordinator(work_item.entity_type)
        outcome = coordinator.run(
            document_id=document_id,
            batch=work_item.batch,
            activity_context=activity_context,
            progress_callback=progress_callback,
            diagnostics_sink=diagnostics_sink,
            budget=budget,
            tables=tables,
        )
        result.partial_results.extend(outcome.partial_results)
        result.attempted_chunk_ids.extend(outcome.attempted_chunk_ids)
        result.unresolved_chunk_ids.extend(outcome.unresolved_chunk_ids)
        result.unresolved_extraction_work.extend(
            UnresolvedExtractionWork(
                chunk_id=chunk_id, entity_type=work_item.entity_type.value
            )
            for chunk_id in outcome.unresolved_chunk_ids
        )

    def _run_windowed_work_item(
        self,
        *,
        document_id: str,
        work_item: ExtractionWorkItem,
        windows: list[TableEvidenceWindow],
        composed_table: TableAsset,
        activity_context: ActivityContext | None,
        progress_callback: Callable[[str], None] | None,
        diagnostics_sink: list[ExtractionBatchDiagnostics],
        result: SpecializedFamilyExtractionRunResult,
        budget: ExtractionExecutionBudget | None = None,
        tables: dict[str, TableAsset] | None = None,
    ) -> None:
        canonical_chunk = work_item.batch.chunks[0]
        original_batch = work_item.batch

        for window in windows:
            if budget is not None and budget.is_expired():
                emit_progress(
                    progress_callback,
                    (
                        f"[extraction {original_batch.batch_index}/"
                        f"{original_batch.batch_count}] "
                        f"[specialized:{work_item.entity_type.value}] "
                        f"{describe_budget_exhaustion(budget)}; skipping window "
                        f"{window.window_index}/{window.window_count} "
                        f"(rows {window.row_start}-{window.row_end})."
                    ),
                )
            # The view-chunk keeps the REAL canonical chunk_id - the model
            # is told (and reports back) this same real id, so existing
            # provenance resolution (chunk_lookup keyed by chunk_id) needs
            # no changes whatsoever. Only `.content` (the bounded window
            # rendering) and the informational table_row_start/end differ
            # from the canonical chunk; the canonical chunk object itself
            # is never mutated (dataclasses.replace returns a new instance).
            view_chunk = dataclass_replace(
                canonical_chunk,
                content=window.rendered_text,
                table_row_start=window.row_start,
                table_row_end=window.row_end,
                chunk_index=window.window_index,
                chunk_total=window.window_count,
            )
            window_batch = ExtractionBatch(
                batch_index=original_batch.batch_index,
                batch_count=original_batch.batch_count,
                chunks=[view_chunk],
                char_count=len(window.rendered_text),
                word_count=len(window.rendered_text.split()),
            )

            coordinator = self._build_coordinator(work_item.entity_type)
            outcome = coordinator.run(
                document_id=document_id,
                batch=window_batch,
                activity_context=activity_context,
                progress_callback=progress_callback,
                diagnostics_sink=diagnostics_sink,
                budget=budget,
                tables=tables,
            )

            # PHASE 2B MAINTENANCE TASK COMPONENT GROUNDING FIX: a narrow,
            # MaintenanceTask-row-window-only deterministic correction --
            # see maintenance_task_component_backfill.py for the confirmed
            # root cause and the exact, non-inventive matching rule. Never
            # applies to any other family; a no-op whenever this window's
            # table has no literal "Item" column or no unambiguous title
            # match, so it cannot affect any other document/table shape.
            if work_item.entity_type == ExtractionPromptType.MAINTENANCE_TASK:
                for partial_result in outcome.partial_results:
                    backfilled = backfill_maintenance_task_component_names(
                        partial_result.maintenance_tasks,
                        table=composed_table,
                        row_start=window.row_start,
                        row_end=window.row_end,
                    )
                    if backfilled and progress_callback is not None:
                        progress_callback(
                            f"Deterministically backfilled component_name for "
                            f"{backfilled} maintenance task(s) in window "
                            f"{window.window_index}/{window.window_count} "
                            "from the source table's 'Item' column."
                        )

            result.partial_results.extend(outcome.partial_results)
            result.attempted_chunk_ids.extend(outcome.attempted_chunk_ids)
            result.unresolved_chunk_ids.extend(outcome.unresolved_chunk_ids)
            result.unresolved_extraction_work.extend(
                UnresolvedExtractionWork(
                    chunk_id=chunk_id,
                    entity_type=work_item.entity_type.value,
                    row_start=window.row_start,
                    row_end=window.row_end,
                )
                for chunk_id in outcome.unresolved_chunk_ids
            )

    def _build_coordinator(self, entity_type) -> ExtractionBatchRetryCoordinator:
        batch_executor = SpecializedExtractionBatchExecutor(
            entity_type=entity_type,
            llm_service=self.llm_service,
            extraction_model=self.extraction_model,
            temperature=self.temperature,
            json_mode=self.json_mode,
            failure_preview_chars=self.failure_preview_chars,
            result_assembler=self.result_assembler,
            num_predict=self.num_predict,
            num_ctx=self.num_ctx,
        )
        return ExtractionBatchRetryCoordinator(
            max_attempts=self.max_attempts,
            allow_partial_batches=self.allow_partial_batches,
            chunk_batcher=self.chunk_batcher,
            batch_executor=batch_executor,
        )
