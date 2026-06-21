from dataclasses import replace

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
from src.domain.retrieval import RetrievalQuery
from src.shared.activity import ActivityContext
from src.shared.exceptions import NoEvidenceFoundError
from src.shared.execution import tracked_action


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
    ) -> RetrievalWorkflowResult:
        validation = self.query_validator.validate(query)
        validation.raise_if_invalid()

        candidate_query = self._candidate_query(query)
        retrieval_result = self.retrieval_service.retrieve(candidate_query)
        deduplication_result = self.retrieved_chunk_deduplicator.deduplicate(
            query=query,
            chunks=retrieval_result.chunks,
        )
        retrieval_result = retrieval_result.__class__(
            result_id=retrieval_result.result_id,
            query=query,
            chunks=deduplication_result.chunks[: query.top_k],
            citations=list(retrieval_result.citations),
            used_dense=retrieval_result.used_dense,
            used_keyword=retrieval_result.used_keyword,
            used_sql=retrieval_result.used_sql,
            total_candidates=len(deduplication_result.chunks),
        )
        enough_evidence = retrieval_result.has_enough_evidence(
            self.min_evidence_chunks
        )

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
            self.context_expander.expand(retrieval_result.chunks, query=query)
            if self.context_expander is not None
            else list(retrieval_result.chunks)
        )

        return RetrievalWorkflowResult(
            retrieval_result=retrieval_result,
            enough_evidence=enough_evidence,
            min_evidence_chunks=self.min_evidence_chunks,
            context_chunks=context_chunks,
        )

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
