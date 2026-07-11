from __future__ import annotations

from typing import TYPE_CHECKING

from src.application.contracts.guardrails.guardrail import Guardrail
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.services.retrieval import HybridRetrievalService
from src.application.validation.retrieval import RetrievalQueryValidator
from src.application.workflows.retrieval.deduplication import (
    RetrievedChunkDeduplicator,
)
from src.application.workflows.retrieval.deduplication.retrieval_deduplication_policy_factory import (
    build_default_retrieval_deduplication_policy,
)
from src.application.workflows.retrieval.retrieval_candidate_pool_sizer import (
    RetrievalCandidatePoolSizer,
)
from src.application.workflows.retrieval.retrieval_workflow_guardrail_adapter import (
    RetrievalWorkflowGuardrailAdapter,
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
from src.application.workflows.retrieval.structured import (
    StructuredEvidenceBundle,
    StructuredEvidenceResolver,
)
from src.application.workflows.shared.document_scope_filter import (
    partition_chunks_by_document_scope,
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
        structured_evidence_resolver: StructuredEvidenceResolver | None = None,
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
                deduplication_policy=build_default_retrieval_deduplication_policy()
            )
        )
        self.candidate_pool_top_k = candidate_pool_top_k
        self.query_analyzer = query_analyzer or RetrievalQueryAnalyzer()
        self.structured_evidence_resolver = structured_evidence_resolver
        self.pre_retrieval_guardrails = pre_retrieval_guardrails or []
        self.post_retrieval_guardrails = post_retrieval_guardrails or []
        self._guardrail_adapter = RetrievalWorkflowGuardrailAdapter(
            min_evidence_chunks=min_evidence_chunks
        )
        self._candidate_pool_sizer = RetrievalCandidatePoolSizer(
            candidate_pool_top_k=candidate_pool_top_k
        )

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
        working_query = (
            query if query.analyzed else self.query_analyzer.analyze(query)
        )
        validation = self.query_validator.validate(working_query)
        validation.raise_if_invalid()
        diagnostics: dict[str, object] = {}
        intent = self.query_analyzer.intent_inferer.resolve(working_query)

        if trace_recorder is not None:
            trace_recorder.record_query_analysis(working_query, intent=intent)

        if self.pre_retrieval_guardrails:
            pre_context = self._guardrail_adapter.build_guardrail_context(
                working_query, intent=intent
            )
            pre_result = self._guardrail_adapter.run_guardrail_chain(
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
                    diagnostics=diagnostics,
                )

        structured_evidence = self._resolve_structured_evidence(working_query)
        if structured_evidence is not None:
            diagnostics.update(structured_evidence.diagnostics)

        candidate_query = self._candidate_pool_sizer.candidate_query(working_query)
        retrieval_result = self._retrieve_candidates(
            candidate_query,
            structured_evidence=structured_evidence,
        )

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
        scoped_retrieval_chunks, discarded_retrieval_chunks = partition_chunks_by_document_scope(
            chunks=retrieval_result.chunks,
            document_id=working_query.document_id,
        )
        if discarded_retrieval_chunks:
            diagnostics["retrieval_scope_discarded_chunk_ids"] = [
                chunk.chunk_id for chunk in discarded_retrieval_chunks
            ]
            diagnostics["retrieval_scope_discarded_document_ids"] = sorted(
                {chunk.document_id for chunk in discarded_retrieval_chunks}
            )
            retrieval_result = retrieval_result.__class__(
                result_id=retrieval_result.result_id,
                query=working_query,
                chunks=scoped_retrieval_chunks,
                citations=list(retrieval_result.citations),
                used_dense=retrieval_result.used_dense,
                used_keyword=retrieval_result.used_keyword,
                used_sql=retrieval_result.used_sql,
                total_candidates=retrieval_result.total_candidates,
            )
        enough_evidence = retrieval_result.has_enough_evidence(
            self.min_evidence_chunks
        )

        post_guardrail_result: GuardrailResult | None = None
        if self.post_retrieval_guardrails:
            post_context = self._guardrail_adapter.build_guardrail_context(
                working_query,
                intent=intent,
                retrieved_chunks=retrieval_result.chunks,
            )
            post_guardrail_result = self._guardrail_adapter.run_guardrail_chain(
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
        context_chunks, discarded_context_chunks = partition_chunks_by_document_scope(
            chunks=context_chunks,
            document_id=working_query.document_id,
        )
        if discarded_context_chunks:
            diagnostics["context_scope_discarded_chunk_ids"] = [
                chunk.chunk_id for chunk in discarded_context_chunks
            ]
            diagnostics["context_scope_discarded_document_ids"] = sorted(
                {chunk.document_id for chunk in discarded_context_chunks}
            )

        if trace_recorder is not None:
            trace_recorder.record_context_expansion(context_chunks)

        return RetrievalWorkflowResult(
            retrieval_result=retrieval_result,
            enough_evidence=enough_evidence,
            min_evidence_chunks=self.min_evidence_chunks,
            context_chunks=context_chunks,
            guardrail_result=post_guardrail_result,
            structured_evidence=structured_evidence,
            diagnostics=diagnostics,
        )

    def _resolve_structured_evidence(
        self,
        query: RetrievalQuery,
    ) -> StructuredEvidenceBundle | None:
        if self.structured_evidence_resolver is None:
            return None
        return self.structured_evidence_resolver.resolve(query)

    def _retrieve_candidates(
        self,
        query: RetrievalQuery,
        *,
        structured_evidence: StructuredEvidenceBundle | None,
    ) -> RetrievalResult:
        additional_candidates = (
            list(structured_evidence.chunks)
            if structured_evidence is not None
            else None
        )
        return self.retrieval_service.retrieve_with_additional_candidates(
            query,
            additional_candidates=additional_candidates,
        )
