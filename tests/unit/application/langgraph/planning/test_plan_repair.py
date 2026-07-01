from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.planning import ExecutionPlan, PlanPolicy, PlanRepair, PlanStep
from src.application.langgraph.state import build_agent_state


def _tool_registry() -> ToolRegistry:
    return ToolRegistry(
        find_document_tool=object(),
        retrieve_chunks_tool=object(),
        retrieve_identifiers_tool=object(),
        answer_question_tool=object(),
        document_details_tool=object(),
    )


def test_plan_repair_renames_retrieve_evidence_tool() -> None:
    result = PlanRepair().repair(
        ExecutionPlan(
            plan_id="plan_1",
            goal="Retrieve evidence",
            steps=[
                PlanStep(
                    step_id="step_1",
                    tool_name="retrieve_evidence",
                    description="Retrieve evidence",
                    output_key="retrieved",
                    args={"query_text": "maintenance interval"},
                    source="llm",
                )
            ],
            reason="repair",
            source="llm",
        ),
        policy=PlanPolicy.default(),
        tool_registry=_tool_registry(),
        state=build_agent_state(user_input="maintenance interval"),
    )

    assert result.repaired is True
    assert result.plan is not None
    assert result.plan.steps[0].tool_name == "retrieve_chunks"


def test_plan_repair_adds_selected_document_id_to_scoped_steps() -> None:
    result = PlanRepair().repair(
        ExecutionPlan(
            plan_id="plan_1",
            goal="Answer",
            steps=[
                PlanStep(
                    step_id="step_1",
                    tool_name="answer_question",
                    description="Answer",
                    output_key="answer",
                    args={"question": "What is the interval?"},
                    source="llm",
                )
            ],
            reason="repair",
            source="llm",
        ),
        policy=PlanPolicy.default(),
        tool_registry=_tool_registry(),
        state=build_agent_state(
            user_input="What is the interval?",
            selected_document_id="doc-42",
        ),
    )

    assert result.repaired is True
    assert result.plan is not None
    assert result.plan.steps[0].args["document_id"] == "doc-42"


def test_plan_repair_removes_blocked_optional_step() -> None:
    result = PlanRepair().repair(
        ExecutionPlan(
            plan_id="plan_1",
            goal="Optional delete",
            steps=[
                PlanStep(
                    step_id="step_1",
                    tool_name="answer_question",
                    description="Answer",
                    output_key="answer",
                    args={"question": "What is the interval?"},
                    source="llm",
                ),
                PlanStep(
                    step_id="step_2",
                    tool_name="delete_document",
                    description="Delete",
                    output_key="deleted",
                    required=False,
                    source="llm",
                ),
            ],
            reason="repair",
            source="llm",
        ),
        policy=PlanPolicy.default(),
        tool_registry=_tool_registry(),
        state=build_agent_state(user_input="What is the interval?"),
    )

    assert result.repaired is True
    assert result.plan is not None
    assert len(result.plan.steps) == 1


def test_plan_repair_preserves_retrieve_identifiers_known_args() -> None:
    result = PlanRepair().repair(
        ExecutionPlan(
            plan_id="plan_1",
            goal="Find part number HP-001",
            steps=[
                PlanStep(
                    step_id="step_1",
                    tool_name="retrieve_identifiers",
                    description="Look up HP-001",
                    output_key="identifier_hits",
                    args={
                        "identifier_value": "HP-001",
                        "identifier_type": "part_number",
                        "unknown_junk": "strip me",
                    },
                    source="llm",
                )
            ],
            reason="identifier",
            source="llm",
        ),
        policy=PlanPolicy.default(),
        tool_registry=_tool_registry(),
        state=build_agent_state(user_input="find part number HP-001"),
    )

    assert result.plan is not None
    step = result.plan.steps[0]
    assert step.tool_name == "retrieve_identifiers"
    assert step.args["identifier_value"] == "HP-001"
    assert step.args["identifier_type"] == "part_number"
    assert "unknown_junk" not in step.args


def test_plan_repair_injects_document_id_into_retrieve_identifiers() -> None:
    result = PlanRepair().repair(
        ExecutionPlan(
            plan_id="plan_1",
            goal="Find identifier",
            steps=[
                PlanStep(
                    step_id="step_1",
                    tool_name="retrieve_identifiers",
                    description="Look up identifier",
                    output_key="identifier_hits",
                    args={"identifier_value": "HP-001"},
                    source="llm",
                )
            ],
            reason="identifier",
            source="llm",
        ),
        policy=PlanPolicy.default(),
        tool_registry=_tool_registry(),
        state=build_agent_state(
            user_input="find HP-001",
            selected_document_id="doc-42",
        ),
    )

    assert result.plan is not None
    assert result.plan.steps[0].args.get("document_id") == "doc-42"


def test_plan_repair_refuses_delete_or_ingest_plan() -> None:
    result = PlanRepair().repair(
        ExecutionPlan(
            plan_id="plan_1",
            goal="Delete docs",
            steps=[
                PlanStep(
                    step_id="step_1",
                    tool_name="delete_document",
                    description="Delete",
                    output_key="deleted",
                    source="llm",
                )
            ],
            reason="repair",
            source="llm",
        ),
        policy=PlanPolicy.default(),
        tool_registry=_tool_registry(),
        state=build_agent_state(user_input="delete documents"),
    )

    assert result.repaired is False
    assert result.plan is None
    assert result.errors
