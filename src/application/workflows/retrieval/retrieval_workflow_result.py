from dataclasses import dataclass

from src.domain.retrieval import RetrievalQuery, RetrievalResult, RetrievedChunk


@dataclass(slots=True)
class RetrievalWorkflowResult:
    retrieval_result: RetrievalResult
    enough_evidence: bool
    min_evidence_chunks: int = 1

    @property
    def query(self) -> RetrievalQuery:
        return self.retrieval_result.query

    @property
    def result_count(self) -> int:
        return len(self.retrieval_result.chunks)

    @property
    def chunks(self) -> list[RetrievedChunk]:
        return self.retrieval_result.chunks

    def has_results(self) -> bool:
        return self.retrieval_result.has_results()

