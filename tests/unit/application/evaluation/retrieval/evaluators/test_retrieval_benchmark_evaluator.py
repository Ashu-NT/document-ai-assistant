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


def test_retrieval_benchmark_evaluator_computes_metrics_and_keeps_anchor_misses_visible() -> None:
    identifier_query = RetrievalQuery(
        query_id="query_identifier",
        query_text="What is the certificate number?",
    )
    semantic_query = RetrievalQuery(
        query_id="query_semantic",
        query_text="How do I run the macerator?",
    )
    context_query = RetrievalQuery(
        query_id="query_context",
        query_text="What is the manual operation caution?",
    )
    workflow = FakeWorkflow(
        {
            "query_identifier": make_workflow_result(
                query=identifier_query,
                anchor_chunks=[
                    make_chunk(
                        chunk_id="chunk_identifier",
                        section_path=["Certificate", "Identity"],
                        score=0.98,
                        content="The certificate serial number is ABC-12345.",
                    ),
                ],
            ),
            "query_semantic": make_workflow_result(
                query=semantic_query,
                anchor_chunks=[
                    make_chunk(
                        chunk_id="chunk_other_1",
                        section_path=["Procedure", "Preparation"],
                        score=0.95,
                    ),
                    make_chunk(
                        chunk_id="chunk_other_2",
                        section_path=["Procedure", "Checklist"],
                        score=0.88,
                    ),
                    make_chunk(
                        chunk_id="chunk_semantic_target",
                        section_path=["Procedure", "Execution"],
                        score=0.86,
                    ),
                ],
            ),
            "query_context": make_workflow_result(
                query=context_query,
                anchor_chunks=[
                    make_chunk(
                        chunk_id="chunk_context_other",
                        section_path=["Safety", "Overview"],
                        score=0.89,
                    ),
                ],
                context_chunks=[
                    make_chunk(
                        chunk_id="chunk_context_other",
                        section_path=["Safety", "Overview"],
                        score=0.89,
                    ),
                    make_chunk(
                        chunk_id="chunk_context_target",
                        section_path=["Operation", "Manual Operation"],
                        score=0.77,
                        content="Caution: manual operation hazard requires trained personnel.",
                    ),
                ],
            ),
        }
    )
    evaluator = RetrievalBenchmarkEvaluator()

    report = evaluator.evaluate(
        workflow,
        [
            make_case(
                query=identifier_query,
                query_type=RetrievalBenchmarkQueryType.IDENTIFIER_LOOKUP,
                rank_target=RetrievalBenchmarkRankTarget.TOP_1,
                expected_chunk_ids=["chunk_identifier"],
                expected_relevant_passage="certificate serial number is ABC-12345",
            ),
            make_case(
                query=semantic_query,
                query_type=RetrievalBenchmarkQueryType.PROCEDURE_LOOKUP,
                rank_target=RetrievalBenchmarkRankTarget.TOP_5,
                expected_section_paths=[["Procedure", "Execution"]],
            ),
            make_case(
                query=context_query,
                query_type=RetrievalBenchmarkQueryType.SAFETY_LOOKUP,
                rank_target=RetrievalBenchmarkRankTarget.TOP_3,
                expected_chunk_ids=["chunk_context_target"],
                expected_relevant_passage="manual operation hazard",
            ),
        ],
    )

    assert workflow.calls == [identifier_query, semantic_query, context_query]
    assert report.case_count == 3
    assert report.hit_rate == 2 / 3
    assert report.mean_reciprocal_rank == (1.0 + (1.0 / 3.0)) / 3.0
    assert report.recall_at_1 == 1 / 3
    assert report.recall_at_3 == 2 / 3
    assert report.recall_at_5 == 2 / 3
    assert report.context_hit_rate == 1.0
    assert report.context_recall_at_3 == 1.0
    assert report.identifier_top_1_accuracy == 1.0
    assert report.section_path_accuracy == 1.0
    assert report.evidence_completeness_rate == 1.0
    assert report.rank_target_satisfaction_rate == 2 / 3

    identifier_result = report.case_results[0]
    semantic_result = report.case_results[1]
    context_result = report.case_results[2]

    assert identifier_result.identifier_top_1_hit is True
    assert identifier_result.meets_expected_rank_target is True
    assert semantic_result.matched_rank == 3
    assert semantic_result.meets_expected_rank_target is True
    assert context_result.hit is False
    assert context_result.context_hit is True
    assert context_result.meets_expected_rank_target is False
    assert context_result.evidence_completeness == 1.0


def test_retrieval_benchmark_evaluator_emits_progress_messages() -> None:
    query = RetrievalQuery(
        query_id="query_progress",
        query_text="What is the identifier?",
    )
    workflow = FakeWorkflow(
        {
            "query_progress": make_workflow_result(
                query=query,
                anchor_chunks=[
                    make_chunk(
                        chunk_id="chunk_progress",
                        section_path=["Certificate", "Identity"],
                        score=0.98,
                    ),
                ],
            )
        }
    )
    evaluator = RetrievalBenchmarkEvaluator()
    messages: list[str] = []

    evaluator.evaluate(
        workflow,
        [
            make_case(
                query=query,
                query_type=RetrievalBenchmarkQueryType.IDENTIFIER_LOOKUP,
                rank_target=RetrievalBenchmarkRankTarget.TOP_1,
                expected_chunk_ids=["chunk_progress"],
            )
        ],
        progress_callback=messages.append,
    )

    assert messages == [
        "[1/1] Running benchmark case query_progress",
        "[1/1] Completed query_progress (anchor_hit=yes, context_hit=yes)",
    ]


def test_evidence_completeness_passage_primary_match() -> None:
    """Passage text found in chunk content → 1.0, regardless of chunk ID or section path."""
    query = RetrievalQuery(query_id="q_passage", query_text="What is the safety procedure?")
    workflow = FakeWorkflow(
        {
            "q_passage": make_workflow_result(
                query=query,
                anchor_chunks=[
                    make_chunk(
                        chunk_id="any_id_stable_or_not",
                        section_path=["Unrelated", "Section"],
                        score=0.90,
                        content="The valve must be closed before purging the system.",
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
            ),
        ],
    )
    assert report.case_results[0].evidence_completeness == 1.0


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
