from src.application.evaluation import (
    RetrievalBenchmarkCase,
    RetrievalBenchmarkEvaluator,
)

from src.application.evaluation.retrieval.benchmarking.enums import (
    RetrievalBenchmarkPriority,
    RetrievalBenchmarkQueryType,
    RetrievalBenchmarkRankTarget,
)

from src.application.workflows.retrieval import RetrievalWorkflowResult

from src.application.workflows.retrieval.retrieval_query_intent import RetrievalQueryIntent

from src.domain.common import ChunkType, SourceLocation

from src.domain.retrieval import RetrievalQuery, RetrievalResult, RetrievedChunk

class FakeWorkflow:
    def __init__(self, results_by_query_id: dict[str, RetrievalWorkflowResult]) -> None:
        self.results_by_query_id = results_by_query_id
        self.calls: list[RetrievalQuery] = []

    def run(self, query: RetrievalQuery) -> RetrievalWorkflowResult:
        self.calls.append(query)
        return self.results_by_query_id[query.query_id]

def make_chunk(
    *,
    chunk_id: str,
    section_path: list[str],
    score: float,
    content: str | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=content if content is not None else f"Content for {chunk_id}",
        score=score,
        retrieval_source="hybrid",
        chunk_type=ChunkType.GENERAL,
        section_id="sec_001",
        section_path=section_path,
        source=SourceLocation(page_start=1, page_end=1),
    )

def make_case(
    *,
    query: RetrievalQuery,
    query_type: RetrievalBenchmarkQueryType,
    rank_target: RetrievalBenchmarkRankTarget,
    expected_chunk_ids: list[str] | None = None,
    expected_section_paths: list[list[str]] | None = None,
    expected_relevant_passage: str | None = None,
    expected_intent: RetrievalQueryIntent | None = None,
) -> RetrievalBenchmarkCase:
    return RetrievalBenchmarkCase(
        case_id=query.query_id,
        query=query,
        query_type=query_type,
        priority=RetrievalBenchmarkPriority.HIGH,
        expected_rank_target=rank_target,
        expected_chunk_ids=expected_chunk_ids or [],
        expected_section_paths=expected_section_paths or [],
        expected_relevant_passage=expected_relevant_passage,
        expected_intent=expected_intent,
    )

def make_workflow_result(
    *,
    query: RetrievalQuery,
    anchor_chunks: list[RetrievedChunk],
    context_chunks: list[RetrievedChunk] | None = None,
) -> RetrievalWorkflowResult:
    return RetrievalWorkflowResult(
        retrieval_result=RetrievalResult(
            result_id=f"result_{query.query_id}",
            query=query,
            chunks=anchor_chunks,
            total_candidates=len(anchor_chunks),
            used_dense=True,
            used_keyword=True,
        ),
        enough_evidence=bool(anchor_chunks),
        min_evidence_chunks=1,
        context_chunks=context_chunks or list(anchor_chunks),
    )

def test_evidence_completeness_section_path_fallback_when_no_passage() -> None:
    """No passage set → section path hit is the fallback → 1.0."""
    query = RetrievalQuery(query_id="q_secpath", query_text="What is the safety procedure?")
    workflow = FakeWorkflow(
        {
            "q_secpath": make_workflow_result(
                query=query,
                anchor_chunks=[
                    make_chunk(
                        chunk_id="new_chunk_id_after_reseed",
                        section_path=["Safety", "Procedures"],
                        score=0.90,
                    ),
                ],
            )
        }
    )
    evaluator = RetrievalBenchmarkEvaluator()
    report = evaluator.evaluate(
        workflow,
        [
            make_case(
                query=query,
                query_type=RetrievalBenchmarkQueryType.SAFETY_LOOKUP,
                rank_target=RetrievalBenchmarkRankTarget.TOP_3,
                expected_section_paths=[["Safety", "Procedures"]],
            ),
        ],
    )
    assert report.case_results[0].evidence_completeness == 1.0

def test_evidence_completeness_zero_when_neither_passage_nor_section_found() -> None:
    query = RetrievalQuery(query_id="q_miss", query_text="Unrelated question?")
    workflow = FakeWorkflow(
        {
            "q_miss": make_workflow_result(
                query=query,
                anchor_chunks=[
                    make_chunk(
                        chunk_id="wrong_chunk",
                        section_path=["Other", "Section"],
                        score=0.5,
                        content="Completely unrelated text about something else.",
                    ),
                ],
            )
        }
    )
    evaluator = RetrievalBenchmarkEvaluator()
    report = evaluator.evaluate(
        workflow,
        [
            make_case(
                query=query,
                query_type=RetrievalBenchmarkQueryType.SAFETY_LOOKUP,
                rank_target=RetrievalBenchmarkRankTarget.TOP_3,
                expected_relevant_passage="valve must be closed before purging",
                expected_section_paths=[["Safety", "Details"]],
            ),
        ],
    )
    assert report.case_results[0].evidence_completeness == 0.0

def test_evaluator_populates_actual_intent_and_flags_correct_and_incorrect_matches() -> None:
    """actual_intent is computed independently of retrieval hit/miss -- it's
    the deterministic RetrievalQueryIntentInferer classifying the case's own
    query text, so it's populated even when expected_intent is unset."""
    safety_query = RetrievalQuery(query_id="q_safety", query_text="What is the safety warning?")
    mismatched_query = RetrievalQuery(
        query_id="q_mismatched", query_text="How do I lubricate the bearing?"
    )
    workflow = FakeWorkflow(
        {
            "q_safety": make_workflow_result(query=safety_query, anchor_chunks=[]),
            "q_mismatched": make_workflow_result(query=mismatched_query, anchor_chunks=[]),
        }
    )
    evaluator = RetrievalBenchmarkEvaluator()

    report = evaluator.evaluate(
        workflow,
        [
            make_case(
                query=safety_query,
                query_type=RetrievalBenchmarkQueryType.SAFETY_LOOKUP,
                rank_target=RetrievalBenchmarkRankTarget.TOP_3,
                expected_intent=RetrievalQueryIntent.SAFETY,
            ),
            make_case(
                query=mismatched_query,
                query_type=RetrievalBenchmarkQueryType.PROCEDURE_LOOKUP,
                rank_target=RetrievalBenchmarkRankTarget.TOP_3,
                expected_intent=RetrievalQueryIntent.PROCEDURE,
            ),
        ],
    )

    safety_result, mismatched_result = report.case_results
    assert safety_result.actual_intent == RetrievalQueryIntent.SAFETY
    assert safety_result.intent_match is True
    assert mismatched_result.actual_intent == RetrievalQueryIntent.MAINTENANCE
    assert mismatched_result.intent_match is False
    assert report.intent_classification_accuracy == 0.5
