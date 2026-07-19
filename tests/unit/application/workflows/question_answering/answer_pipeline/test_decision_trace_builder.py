from src.application.services.answer_generation.answer_generation_result import (
    GeneratedAnswer,
)
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_pipeline.decision_trace_builder import (
    build_decision_trace,
)
from src.domain.retrieval import RetrievalQuery


def _query(**overrides) -> RetrievalQuery:
    defaults = dict(query_id="q_1", query_text="test")
    defaults.update(overrides)
    return RetrievalQuery(**defaults)


def _answer(**overrides) -> GeneratedAnswer:
    defaults = dict(
        answer_text="answer",
        citations=[],
        cited_chunk_ids=[],
        prompt_version="v1",
        model_name="qwen3:8b",
        diagnostics={},
    )
    defaults.update(overrides)
    return GeneratedAnswer(**defaults)


def test_build_decision_trace_carries_the_retrieval_side_classification() -> None:
    query = _query(
        detected_intent="table",
        intent_best_score=6,
        intent_runner_up_score=6,
        intent_score_gap=0,
        intent_confidence=0.62,
        intent_runner_up="troubleshooting",
    )
    generated = _answer()

    trace = build_decision_trace(analyzed_query=query, generated=generated)

    assert trace["retrieval_intent"] == "table"
    assert trace["retrieval_intent_best_score"] == 6
    assert trace["retrieval_intent_runner_up"] == "troubleshooting"
    assert trace["retrieval_intent_runner_up_score"] == 6
    assert trace["retrieval_intent_gap"] == 0


def test_build_decision_trace_carries_the_answer_side_classification() -> None:
    query = _query()
    generated = _answer(
        answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        diagnostics={
            "answer_intent_best_score": 8,
            "answer_intent_runner_up": "table_summary",
            "answer_intent_runner_up_score": 2,
            "answer_intent_margin": 6,
        },
    )

    trace = build_decision_trace(analyzed_query=query, generated=generated)

    assert trace["answer_intent"] == "identifier_lookup"
    assert trace["answer_intent_best_score"] == 8
    assert trace["answer_intent_runner_up"] == "table_summary"
    assert trace["answer_intent_runner_up_score"] == 2
    assert trace["answer_intent_margin"] == 6


def test_build_decision_trace_reports_the_llm_path_when_no_renderer_fired() -> None:
    query = _query()
    generated = _answer(
        diagnostics={
            "deterministic_dispatch_bypassed": True,
            "deterministic_dispatch_bypass_reason": "contested_intent",
        },
    )

    trace = build_decision_trace(analyzed_query=query, generated=generated)

    assert trace["deterministic_bypassed"] is True
    assert trace["bypass_reason"] == "contested_intent"
    assert trace["renderer_used"] is None
    assert trace["llm_used"] is True


def test_build_decision_trace_reports_the_renderer_path_when_one_fired() -> None:
    query = _query()
    generated = _answer(
        diagnostics={
            "deterministic_dispatch_bypassed": False,
            "deterministic_renderer": "deterministic_identifier_renderer",
        },
    )

    trace = build_decision_trace(analyzed_query=query, generated=generated)

    assert trace["deterministic_bypassed"] is False
    assert trace["renderer_used"] == "deterministic_identifier_renderer"
    assert trace["llm_used"] is False


def test_build_decision_trace_handles_a_decision_with_no_runner_up_at_all() -> None:
    query = _query(detected_intent="maintenance")
    generated = _answer()

    trace = build_decision_trace(analyzed_query=query, generated=generated)

    assert trace["retrieval_intent"] == "maintenance"
    assert trace["retrieval_intent_runner_up"] is None
    assert trace["retrieval_intent_gap"] is None
    assert trace["answer_intent"] is None
