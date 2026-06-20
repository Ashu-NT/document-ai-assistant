from src.application.workflows.retrieval import (
    ChunkQualityEvaluator,
    RetrievalBenchmarkCase,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.retrieval import RetrievalQuery, RetrievalResult, RetrievedChunk


class FakeWorkflow:
    def __init__(self, results_by_query_id: dict[str, RetrievalResult]) -> None:
        self.results_by_query_id = results_by_query_id
        self.calls: list[RetrievalQuery] = []

    def run(self, query: RetrievalQuery) -> RetrievalResult:
        self.calls.append(query)
        return self.results_by_query_id[query.query_id]


def make_chunk(
    *,
    chunk_id: str,
    section_path: list[str],
    score: float,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=f"Content for {chunk_id}",
        score=score,
        retrieval_source="dense",
        chunk_type=ChunkType.GENERAL,
        section_id="sec_001",
        section_path=section_path,
        source=SourceLocation(page_start=1, page_end=1),
    )


def test_chunk_quality_evaluator_reports_hit_rate_and_mrr() -> None:
    query_one = RetrievalQuery(query_id="query_001", query_text="First query")
    query_two = RetrievalQuery(query_id="query_002", query_text="Second query")
    workflow = FakeWorkflow(
        {
            "query_001": RetrievalResult(
                result_id="result_001",
                query=query_one,
                chunks=[
                    make_chunk(
                        chunk_id="chunk_expected_001",
                        section_path=["Procedure", "Execution"],
                        score=0.91,
                    ),
                ],
            ),
            "query_002": RetrievalResult(
                result_id="result_002",
                query=query_two,
                chunks=[
                    make_chunk(
                        chunk_id="chunk_other_001",
                        section_path=["Procedure", "Preparation"],
                        score=0.88,
                    ),
                    make_chunk(
                        chunk_id="chunk_other_002",
                        section_path=["Procedure", "Execution"],
                        score=0.79,
                    ),
                ],
            ),
        }
    )
    evaluator = ChunkQualityEvaluator()

    report = evaluator.evaluate(
        workflow,
        [
            RetrievalBenchmarkCase(
                query=query_one,
                expected_chunk_ids=["chunk_expected_001"],
            ),
            RetrievalBenchmarkCase(
                query=query_two,
                expected_section_paths=[["Procedure", "Execution"]],
            ),
        ],
    )

    assert workflow.calls == [query_one, query_two]
    assert report.case_count == 2
    assert report.hit_rate == 1.0
    assert report.mean_reciprocal_rank == 0.75
    assert report.average_relevant_hits == 1.0
