from src.application.agent_runtime.policies import DemoVisibilityPolicy
from src.application.agent_runtime.react_loop import ReactTraceBuilder
from src.application.langgraph.common import GraphResult


def test_answer_question_maps_to_safe_thought_summary() -> None:
    builder = ReactTraceBuilder()
    result = GraphResult.ok(response_text="Answer", route="answer_question", data={})

    trace = builder.build(
        user_input="What is the maintenance interval?",
        result=result,
        policy=DemoVisibilityPolicy(),
    )

    assert trace.steps[0].body.startswith("The request asks for document evidence")


def test_deep_research_maps_to_research_thought_summary() -> None:
    builder = ReactTraceBuilder()
    result = GraphResult.ok(response_text="Answer", route="deep_research", data={})

    trace = builder.build(
        user_input="Compare maintenance tasks and specifications",
        result=result,
        policy=DemoVisibilityPolicy(),
    )

    assert "synthesis across evidence groups" in trace.steps[0].body


def test_blocked_action_maps_to_safety_block() -> None:
    builder = ReactTraceBuilder()
    result = GraphResult.ok(
        response_text="Blocked.",
        route="blocked_action",
        data={"unsafe_request_blocked": True, "blocked_reason": "Unsafe request."},
    )

    trace = builder.build(
        user_input="Delete the corpus",
        result=result,
        policy=DemoVisibilityPolicy(),
    )

    assert any(step.title == "Safety Block" for step in trace.steps)


def test_research_plan_becomes_react_step() -> None:
    builder = ReactTraceBuilder()
    result = GraphResult.ok(
        response_text="Answer",
        route="deep_research",
        data={"research_plan": {"tasks": [{"title": "Collect maintenance tasks"}]}},
    )

    trace = builder.build(
        user_input="Generate a maintenance report",
        result=result,
        policy=DemoVisibilityPolicy(),
    )

    assert any(step.title == "Research Plan" for step in trace.steps)


def test_retrieval_strategy_becomes_react_step() -> None:
    builder = ReactTraceBuilder()
    result = GraphResult.ok(
        response_text="Answer",
        route="answer_question",
        data={"retrieval_strategy_decision": {"primary_strategy": "MAINTENANCE_LOOKUP"}},
    )

    trace = builder.build(
        user_input="Question",
        result=result,
        policy=DemoVisibilityPolicy(),
    )

    assert any(step.title == "Retrieval Strategy" for step in trace.steps)


def test_missing_retrieval_strategy_does_not_print_failure_text() -> None:
    builder = ReactTraceBuilder()
    result = GraphResult.ok(response_text="Answer", route="answer_question", data={})

    trace = builder.build(
        user_input="Question",
        result=result,
        policy=DemoVisibilityPolicy(),
    )

    assert all("No retrieval strategy decision was recorded" not in step.body for step in trace.steps)


def test_reflection_result_becomes_react_step() -> None:
    builder = ReactTraceBuilder()
    result = GraphResult.ok(
        response_text="Answer",
        route="answer_question",
        data={
            "reflection_result": {
                "decision": {"decision": "ACCEPT", "reason": "Grounded."}
            },
            "reflection_score": 0.92,
        },
    )

    trace = builder.build(
        user_input="Question",
        result=result,
        policy=DemoVisibilityPolicy(),
    )

    assert any(step.title == "Reflection" for step in trace.steps)


def test_raw_prompts_and_internal_ids_are_hidden() -> None:
    builder = ReactTraceBuilder()
    result = GraphResult.ok(
        response_text="Answer",
        route="answer_question",
        data={
            "raw_llm_plan": '{"secret":"plan"}',
            "selected_document_id": "doc_secret",
            "context_chunks": [{"document_id": "doc_secret", "content": "Evidence"}],
        },
    )

    trace = builder.build(
        user_input="Question",
        result=result,
        policy=DemoVisibilityPolicy(),
    )

    rendered = "\n".join(step.body for step in trace.steps)
    assert "secret" not in rendered
    assert "doc_secret" not in rendered
    assert "chain-of-thought" not in rendered
