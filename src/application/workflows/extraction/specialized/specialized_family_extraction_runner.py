from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

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
from src.application.workflows.extraction.candidates.extraction_candidate_selector import (
    ExtractionCandidateSelector,
)
from src.application.workflows.extraction.extraction_result_assembler import (
    ExtractionResultAssembler,
)
from src.application.workflows.extraction.specialized.extraction_plan import (
    build_extraction_plan,
)
from src.application.workflows.extraction.specialized.specialized_extraction_batch_executor import (
    SpecializedExtractionBatchExecutor,
)
from src.domain.extraction import ExtractionResult, UnresolvedExtractionWork
from src.shared.activity import ActivityContext

# Top-level SPECIALIZED_FAMILY orchestrator: given the SAME batches
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

    def run(
        self,
        *,
        document_id: str,
        batches: list[ExtractionBatch],
        activity_context: ActivityContext | None,
        progress_callback: Callable[[str], None] | None,
        diagnostics_sink: list[ExtractionBatchDiagnostics],
    ) -> SpecializedFamilyExtractionRunResult:
        plan = build_extraction_plan(
            batches, candidate_selector=self.candidate_selector
        )
        result = SpecializedFamilyExtractionRunResult()

        for work_item in plan.work_items:
            batch_executor = SpecializedExtractionBatchExecutor(
                entity_type=work_item.entity_type,
                llm_service=self.llm_service,
                extraction_model=self.extraction_model,
                temperature=self.temperature,
                json_mode=self.json_mode,
                failure_preview_chars=self.failure_preview_chars,
                result_assembler=self.result_assembler,
            )
            coordinator = ExtractionBatchRetryCoordinator(
                max_attempts=self.max_attempts,
                allow_partial_batches=self.allow_partial_batches,
                chunk_batcher=self.chunk_batcher,
                batch_executor=batch_executor,
            )
            outcome = coordinator.run(
                document_id=document_id,
                batch=work_item.batch,
                activity_context=activity_context,
                progress_callback=progress_callback,
                diagnostics_sink=diagnostics_sink,
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

        return result
