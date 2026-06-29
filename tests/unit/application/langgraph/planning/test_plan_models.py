from src.application.langgraph.planning import ExecutionPlan, PlanStep


def test_plan_step_serializes_to_dict() -> None:
    step = PlanStep(
        step_id="step_1",
        tool_name="answer_question",
        description="Answer the question.",
        input_key="input_a",
        output_key="answer",
        args={"question": "What is the maintenance interval?"},
        depends_on=["find_document"],
        required=True,
    )

    payload = step.to_dict()

    assert payload["step_id"] == "step_1"
    assert payload["tool_name"] == "answer_question"
    assert payload["description"] == "Answer the question."
    assert payload["input_key"] == "input_a"
    assert payload["output_key"] == "answer"
    assert payload["args"] == {"question": "What is the maintenance interval?"}
    assert payload["depends_on"] == ["find_document"]
    assert payload["required"] is True


def test_execution_plan_reports_step_count_and_tool_names() -> None:
    plan = ExecutionPlan(
        plan_id="plan_1",
        goal="compare specifications and maintenance tasks",
        steps=[
            PlanStep(
                step_id="step_1",
                tool_name="answer_question",
                description="Answer specifications.",
                output_key="answer_1",
            ),
            PlanStep(
                step_id="step_2",
                tool_name="answer_question",
                description="Answer maintenance.",
                output_key="answer_2",
            ),
        ],
        reason="Detected a comparison request.",
    )

    assert plan.is_empty is False
    assert plan.step_count == 2
    assert plan.tool_names == ["answer_question", "answer_question"]
    assert plan.to_dict()["goal"] == "compare specifications and maintenance tasks"
