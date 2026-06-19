from src.application.services.retrieval import HybridRetrievalService
from src.application.validation.retrieval import RetrievalQueryValidator
from src.application.workflows.retrieval.retrieval_workflow_result import (
    RetrievalWorkflowResult,
)
from src.domain.retrieval import RetrievalQuery
from src.shared.activity import ActivityContext
from src.shared.exceptions import NoEvidenceFoundError
from src.shared.execution import tracked_action


class RetrievalWorkflow:
    def __init__(
        self,
        retrieval_service: HybridRetrievalService,
        query_validator: RetrievalQueryValidator,
        min_evidence_chunks: int = 1,
        strict_evidence: bool = False,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.query_validator = query_validator
        self.min_evidence_chunks = min_evidence_chunks
        self.strict_evidence = strict_evidence

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

        retrieval_result = self.retrieval_service.retrieve(query)
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

        return RetrievalWorkflowResult(
            retrieval_result=retrieval_result,
            enough_evidence=enough_evidence,
            min_evidence_chunks=self.min_evidence_chunks,
        )
