from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from src.application.contracts.guardrails.guardrail import Guardrail
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.services.retrieval import HybridRetrievalService
from src.application.validation.retrieval import RetrievalQueryValidator
from src.application.workflows.retrieval.deduplication import (
    RetrievedChunkDeduplicator,
    RetrievalDeduplicationPolicy,
)
from src.application.workflows.retrieval.retrieval_workflow_result import (
    RetrievalWorkflowResult,
)
from src.application.workflows.retrieval.retrieval_context_expander import (
    RetrievalContextExpander,
)
from src.application.workflows.retrieval.retrieval_query_analyzer import (
    RetrievalQueryAnalyzer,
)
from src.domain.common import new_id
from src.domain.retrieval import RetrievalQuery, RetrievalResult
from src.shared.activity import ActivityContext
from src.shared.exceptions import NoEvidenceFoundError
from src.shared.execution import tracked_action

if TYPE_CHECKING:
    from src.application.workflows.retrieval.tracing.retrieval_trace_recorder import (
        RetrievalTraceRecorder,
    )


def _default_retrieval_deduplication_policy() -> RetrievalDeduplicationPolicy:
    try:
        from src.config.settings import retrieval_settings

        return RetrievalDeduplicationPolicy(
            exact_duplicate_enabled=retrieval_settings.exact_duplicate_enabled,
            context_companion_collapse_enabled=(
                retrieval_settings.context_companion_collapse_enabled
            ),
            overview_duplicate_collapse_enabled=(
                retrieval_settings.overview_duplicate_collapse_enabled
            ),
            token_overlap_threshold=retrieval_settings.token_overlap_threshold,
            containment_threshold=retrieval_settings.containment_threshold,
            min_unique_token_count=retrieval_settings.min_unique_token_count,
        )
    except Exception:
        return RetrievalDeduplicationPolicy()


def _default_candidate_pool_top_k() -> int:
    try:
        from src.config.settings import retrieval_settings

        return max(
            retrieval_settings.final_retrieval_top_k,
            retrieval_settings.dense_retrieval_top_k,
            retrieval_settings.keyword_retrieval_top_k,
            retrieval_settings.sql_retrieval_top_k,
        )
    except Exception:
        return 10


class RetrievalWorkflow:
    def __init__(
        self,
        retrieval_service: HybridRetrievalService,
        query_validator: RetrievalQueryValidator,
        min_evidence_chunks: int = 1,
        strict_evidence: bool = False,
        context_expander: RetrievalContextExpander | None = None,
        retrieved_chunk_deduplicator: RetrievedChunkDeduplicator | None = None,
        candidate_pool_top_k: int | None = None,
        query_analyzer: RetrievalQueryAnalyzer | None = None,
        pre_retrieval_guardrails: list[Guardrail] | None = None,
        post_retrieval_guardrails: list[Guardrail] | None = None,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.query_validator = query_validator
        self.min_evidence_chunks = min_evidence_chunks
        self.strict_evidence = strict_evidence
        self.context_expander = context_expander
        self.retrieved_chunk_deduplicator = (
            retrieved_chunk_deduplicator
            or RetrievedChunkDeduplicator(
                deduplication_policy=_default_retrieval_deduplication_policy()
            )
        )
        self.candidate_pool_top_k = candidate_pool_top_k
        self.query_analyzer = query_analyzer or RetrievalQueryAnalyzer()
        self.pre_retrieval_guardrails = pre_retrieval_guardrails or []
        self.post_retrieval_guardrails = post_retrieval_guardrails or []

    @tracked_action(
        action="retrieval.workflow_completed",
        entity_type="retrieval_query",
        activity=True,
        audit=False,
        event=False,
    )
    def run(
        self,
        query: RetrievalQuery,
        activity_context: ActivityContext | None = None,
        trace_recorder: RetrievalTraceRecorder | None = None,
    ) -> RetrievalWorkflowResult:
        working_query = self.query_analyzer.analyze(query)
        validation = self.query_validator.validate(working_query)
        validation.raise_if_invalid()

        if trace_recorder is not None:
            trace_recorder.record_query_analysis(working_query)

        if self.pre_retrieval_guardrails:
            pre_context = self._build_guardrail_context(working_query)
            pre_result = self._run_guardrail_chain(
                self.pre_retrieval_guardrails, pre_context
            )
            if trace_recorder is not None:
                trace_recorder.record_pre_guardrail(pre_result)
            if pre_result is not None and not pre_result.allowed:
                empty_result = RetrievalResult(
                    result_id=new_id("gr"),
                    query=working_query,
                    chunks=[],
                    citations=[],
                )
                return RetrievalWorkflowResult(
                    retrieval_result=empty_result,
                    enough_evidence=False,
                    min_evidence_chunks=self.min_evidence_chunks,
                    context_chunks=[],
                    guardrail_result=pre_result,
                )

        candidate_query = self._candidate_query(working_query)
        retrieval_result = self.retrieval_service.retrieve(candidate_query)

        if trace_recorder is not None:
            trace_recorder.record_candidates(retrieval_result.chunks)

        deduplication_result = self.retrieved_chunk_deduplicator.deduplicate(
            query=working_query,
            chunks=retrieval_result.chunks,
        )
        final_chunks = deduplication_result.chunks[: working_query.top_k]

        if trace_recorder is not None:
            trace_recorder.record_dedup(
                before_count=len(retrieval_result.chunks),
                after_chunks=final_chunks,
            )

        retrieval_result = retrieval_result.__class__(
            result_id=retrieval_result.result_id,
            query=working_query,
            chunks=final_chunks,
            citations=list(retrieval_result.citations),
            used_dense=retrieval_result.used_dense,
            used_keyword=retrieval_result.used_keyword,
            used_sql=retrieval_result.used_sql,
            total_candidates=len(deduplication_result.chunks),
        )
        enough_evidence = retrieval_result.has_enough_evidence(
            self.min_evidence_chunks
        )

        post_guardrail_result: GuardrailResult | None = None
        if self.post_retrieval_guardrails:
            post_context = self._build_guardrail_context(
                working_query,
                retrieved_chunks=retrieval_result.chunks,
            )
            post_guardrail_result = self._run_guardrail_chain(
                self.post_retrieval_guardrails, post_context
            )
            if trace_recorder is not None:
                trace_recorder.record_post_guardrail(post_guardrail_result)

        if self.strict_evidence and not retrieval_result.has_results():
            raise NoEvidenceFoundError(
                "No retrieval evidence found.",
                details={
                    "query_id": query.query_id,
                    "min_evidence_chunks": self.min_evidence_chunks,
                },
            )

        if self.strict_evidence and not enough_evidence:
            raise NoEvidenceFoundError(
                "Not enough retrieval evidence found.",
                details={
                    "query_id": query.query_id,
                    "result_count": len(retrieval_result.chunks),
                    "min_evidence_chunks": self.min_evidence_chunks,
                },
            )

        context_chunks = (
            self.context_expander.expand(
                retrieval_result.chunks,
                query=working_query,
            )
            if self.context_expander is not None
            else list(retrieval_result.chunks)
        )

        if trace_recorder is not None:
            trace_recorder.record_context_expansion(context_chunks)

        return RetrievalWorkflowResult(
            retrieval_result=retrieval_result,
            enough_evidence=enough_evidence,
            min_evidence_chunks=self.min_evidence_chunks,
            context_chunks=context_chunks,
            guardrail_result=post_guardrail_result,
        )

    def _build_guardrail_context(
        self,
        working_query: RetrievalQuery,
        retrieved_chunks: list | None = None,
    ) -> GuardrailContext:
        intent = self.query_analyzer.intent_inferer.infer(working_query)
        return GuardrailContext(
            query_text=working_query.query_text,
            detected_identifiers=list(working_query.detected_identifiers),
            query_intent=str(intent),
            query_chunk_types=[ct.value for ct in working_query.chunk_types],
            retrieved_chunks=retrieved_chunks or [],
            min_evidence_chunks=self.min_evidence_chunks,
        )

    @staticmethod
    def _run_guardrail_chain(
        guardrails: list[Guardrail],
        context: GuardrailContext,
    ) -> GuardrailResult | None:
        for guardrail in guardrails:
            result = guardrail.check(context)
            if not result.allowed:
                return result
        return None

    def _candidate_query(
        self,
        query: RetrievalQuery,
    ) -> RetrievalQuery:
        candidate_pool_top_k = max(
            query.top_k,
            self.candidate_pool_top_k or _default_candidate_pool_top_k(),
        )
        if candidate_pool_top_k == query.top_k:
            return query
        return replace(query, top_k=candidate_pool_top_k)
