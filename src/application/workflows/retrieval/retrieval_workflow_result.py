from dataclasses import dataclass

from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.domain.retrieval import RetrievalQuery, RetrievalResult, RetrievedChunk


@dataclass(slots=True)
class RetrievalWorkflowResult:
    retrieval_result: RetrievalResult
    enough_evidence: bool
    min_evidence_chunks: int = 1
    context_chunks: list[RetrievedChunk] | None = None
    guardrail_result: GuardrailResult | None = None

    @property
    def query(self) -> RetrievalQuery:
        return self.retrieval_result.query

    @property
    def result_count(self) -> int:
        return len(self.retrieval_result.chunks)

    @property
    def chunks(self) -> list[RetrievedChunk]:
        return self.retrieval_result.chunks

    @property
    def final_chunks(self) -> list[RetrievedChunk]:
        return self.context_chunks or self.retrieval_result.chunks

    @property
    def context_result_count(self) -> int:
        return len(self.final_chunks)

    def has_results(self) -> bool:
        return self.retrieval_result.has_results()
