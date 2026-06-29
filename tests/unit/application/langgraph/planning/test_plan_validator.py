from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.planning import ExecutionPlan, PlanPolicy, PlanStep, PlanValidator
from src.application.langgraph.state import build_agent_state


def _tool_registry() -> ToolRegistry:
    return ToolRegistry(
        list_documents_tool=object(),
        find_document_tool=object(),
        document_details_tool=object(),
        explore_document_tool=object(),
        retrieve_chunks_tool=object(),
        answer_question_tool=object(),
        run_quality_gate_tool=object(),
        retrieval_trace_tool=object(),
    )


def test_plan_validator_rejects_unknown_tool() -> None:
    result = PlanValidator().validate(
        ExecutionPlan(
            plan_id="plan_1",
            goal="Unknown tool",
            steps=[
                PlanStep(
                    step_id="step_1",
                    tool_name="shell_execute",
                    description="Unsafe tool",
                    output_key="x",
                )
            ],
            reason="bad",
            source="llm",
        ),
        policy=PlanPolicy.default(),
        tool_registry=_tool_registry(),
        state=build_agent_state(user_input="do something"),
    )

    assert result.success is False
    assert any("not allowed" in error for error in result.errors)


def test_plan_validator_rejects_blocked_tool() -> None:
    result = PlanValidator().validate(
        ExecutionPlan(
            plan_id="plan_1",
            goal="Delete docs",
            steps=[
                PlanStep(
                    step_id="step_1",
                    tool_name="delete_document",
                    description="Delete a document",
                    output_key="deleted",
                    source="llm",
                )
            ],
            reason="bad",
            source="llm",
        ),
        policy=PlanPolicy.default(),
        tool_registry=_tool_registry(),
        state=build_agent_state(user_input="delete document"),
    )

    assert result.success is False
    assert any("blocked" in error for error in result.errors)


def test_plan_validator_rejects_excessive_steps_and_duplicate_ids() -> None:
    steps = [
        PlanStep(
            step_id="step_1",
            tool_name="list_documents",
            description="List docs",
            output_key=f"output_{index}",
            source="llm",
        )
        for index in range(6)
    ]
    steps[1] = PlanStep(
        step_id="step_1",
        tool_name="list_documents",
        description="Duplicate id",
        output_key="output_dup",
        source="llm",
    )
    result = PlanValidator().validate(
        ExecutionPlan(
            plan_id="plan_1",
            goal="Too many steps",
            steps=steps,
            reason="bad",
            source="llm",
        ),
        policy=PlanPolicy.default(),
        tool_registry=_tool_registry(),
        state=build_agent_state(user_input="list many documents"),
    )

    assert result.success is False
    assert any("maximum allowed step count" in error for error in result.errors)
    assert any("Duplicate step_id" in error for error in result.errors)


def test_plan_validator_rejects_missing_dependency() -> None:
    result = PlanValidator().validate(
        ExecutionPlan(
            plan_id="plan_1",
            goal="Bad dependency",
            steps=[
                PlanStep(
                    step_id="step_1",
                    tool_name="answer_question",
                    description="Answer",
                    output_key="answer",
                    args={"question": "What is the maintenance interval?"},
                    depends_on=["missing_step"],
                    source="llm",
                )
            ],
            reason="bad",
            source="llm",
        ),
        policy=PlanPolicy.default(),
        tool_registry=_tool_registry(),
        state=build_agent_state(
            user_input="What is the maintenance interval?",
            selected_document_id="doc-42",
        ),
    )

    assert result.success is False
    assert any("existing previous step_id" in error for error in result.errors)


def test_plan_validator_rejects_document_mismatch() -> None:
    result = PlanValidator().validate(
        ExecutionPlan(
            plan_id="plan_1",
            goal="Wrong document",
            steps=[
                PlanStep(
                    step_id="step_1",
                    tool_name="answer_question",
                    description="Answer",
                    output_key="answer",
                    args={
                        "question": "What is the maintenance interval?",
                        "document_id": "doc-other",
                    },
                    source="llm",
                )
            ],
            reason="bad",
            source="llm",
        ),
        policy=PlanPolicy.default(),
        tool_registry=_tool_registry(),
        state=build_agent_state(
            user_input="What is the maintenance interval?",
            selected_document_id="doc-42",
        ),
    )

    assert result.success is False
    assert any("does not match the selected document" in error for error in result.errors)


def test_plan_validator_accepts_valid_retrieve_and_answer_plan() -> None:
    result = PlanValidator().validate(
        ExecutionPlan(
            plan_id="plan_1",
            goal="Retrieve and answer",
            steps=[
                PlanStep(
                    step_id="step_1",
                    tool_name="retrieve_chunks",
                    description="Retrieve evidence",
                    output_key="retrieved_evidence",
                    args={"query_text": "maintenance interval", "document_id": "doc-42"},
                    source="llm",
                ),
                PlanStep(
                    step_id="step_2",
                    tool_name="answer_question",
                    description="Answer the question",
                    output_key="answer",
                    args={"question": "What is the maintenance interval?", "document_id": "doc-42"},
                    depends_on=["step_1"],
                    source="llm",
                ),
            ],
            reason="good",
            source="llm",
        ),
        policy=PlanPolicy.default(),
        tool_registry=_tool_registry(),
        state=build_agent_state(
            user_input="What is the maintenance interval?",
            selected_document_id="doc-42",
        ),
    )

    assert result.success is True
    assert result.validated_plan is not None
