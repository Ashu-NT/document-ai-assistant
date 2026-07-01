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


def test_retrieval_strategy_step_renders_guarded_advisor_details() -> None:
    builder = ReactTraceBuilder()
    result = GraphResult.ok(
        response_text="Answer",
        route="deep_research",
        data={
            "strategy_advisor_result": {
                "status": "accepted",
                "proposal": {
                    "route": "deep_research",
                    "concepts": ["fault recovery", "scheduled servicing"],
                    "recommended_strategies": [
                        "TROUBLESHOOTING_LOOKUP",
                        "MAINTENANCE_LOOKUP",
                    ],
                    "reason": "The request compares two maintenance-related concepts.",
                },
            },
            "strategy_advisor_trace": {
                "events": [
                    {"name": "StrategyAdvisorStarted"},
                    {"name": "StrategyAdvisorCompleted"},
                    {"name": "StrategyValidated"},
                    {"name": "StrategyMerged"},
                ]
            },
        },
    )

    trace = builder.build(
        user_input="contrast fault recovery with scheduled servicing",
        result=result,
        policy=DemoVisibilityPolicy(),
    )

    retrieval_step = next(step for step in trace.steps if step.title == "Retrieval Strategy")
    assert "Advisor: accepted" in retrieval_step.body
    assert "fault recovery" in retrieval_step.body
    assert "StrategyAdvisorStarted" in retrieval_step.body


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


def test_deep_research_strategy_coverage_becomes_reflection_step() -> None:
    builder = ReactTraceBuilder()
    result = GraphResult.ok(
        response_text="Answer",
        route="deep_research",
        data={
            "research_trace": {
                "strategy_coverage": {
                    "ratio": 0.67,
                    "covered_concepts": ["maintenance", "procedures"],
                    "uncovered_concepts": ["troubleshooting"],
                    "passed": False,
                }
            }
        },
    )

    trace = builder.build(
        user_input="compare maintenance procedures and troubleshooting",
        result=result,
        policy=DemoVisibilityPolicy(),
    )

    reflection_step = next(step for step in trace.steps if step.title == "Reflection")
    assert "REPLAN_REQUIRED" in reflection_step.body
    assert "Concept coverage" in reflection_step.body
    assert "troubleshooting" in reflection_step.body


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
