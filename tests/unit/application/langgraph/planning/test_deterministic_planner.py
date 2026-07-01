from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.planning import (
    DeterministicPlanner,
    PlanPolicy,
    PlanValidator,
)
from src.application.langgraph.state import build_agent_state


def _full_tool_registry() -> ToolRegistry:
    return ToolRegistry(
        list_documents_tool=object(),
        find_document_tool=object(),
        document_details_tool=object(),
        explore_document_tool=object(),
        retrieve_chunks_tool=object(),
        retrieve_identifiers_tool=object(),
        answer_question_tool=object(),
        run_quality_gate_tool=object(),
        retrieval_trace_tool=object(),
    )


# ---------------------------------------------------------------------------
# Identifier lookup plans
# ---------------------------------------------------------------------------

def test_planner_creates_identifier_lookup_plan_for_part_number() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(user_input="find part number HP-001")
    )

    assert plan is not None
    assert "retrieve_identifiers" in plan.tool_names
    assert plan.tool_names[0] == "retrieve_identifiers"


def test_planner_identifier_plan_ends_with_answer_question() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(user_input="what is part number HP-001")
    )

    assert plan is not None
    assert plan.tool_names[-1] == "answer_question"


def test_planner_identifier_plan_captures_identifier_value_in_diagnostics() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(user_input="find part number HP-001")
    )

    assert plan is not None
    assert plan.diagnostics.get("identifier_value") == "HP-001"


def test_planner_identifier_plan_infers_part_number_type() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(user_input="find part number HP-001")
    )

    assert plan is not None
    first_step = plan.steps[0]
    assert first_step.args.get("identifier_type") == "part_number"


def test_planner_identifier_plan_infers_serial_number_type() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(user_input="find serial number SN-2024-001")
    )

    assert plan is not None
    first_step = plan.steps[0]
    assert first_step.args.get("identifier_type") == "serial_number"


def test_planner_identifier_maintenance_plan_adds_retrieve_chunks() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(
            user_input="what maintenance tasks reference HP-001",
            selected_document_id="doc-42",
        )
    )

    assert plan is not None
    tool_names = plan.tool_names
    assert "retrieve_identifiers" in tool_names
    assert "retrieve_chunks" in tool_names
    assert "answer_question" in tool_names


def test_planner_identifier_specification_plan_adds_retrieve_chunks() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(
            user_input="what are the specifications for FLT-100",
            selected_document_id="doc-42",
        )
    )

    assert plan is not None
    tool_names = plan.tool_names
    assert "retrieve_identifiers" in tool_names
    assert "retrieve_chunks" in tool_names


def test_planner_identifier_plan_scopes_to_selected_document() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(
            user_input="find serial number SN-001",
            selected_document_id="doc-99",
        )
    )

    assert plan is not None
    first_step = plan.steps[0]
    assert first_step.args.get("document_id") == "doc-99"


def test_planner_identifier_plan_infers_certificate_number_type() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(user_input="find certificate number ISO-9001")
    )

    assert plan is not None
    first_step = plan.steps[0]
    assert first_step.args.get("identifier_type") == "certificate_number"


def test_planner_identifier_plan_infers_manufacturer_name_type() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(user_input="who is the manufacturer of this pump")
    )

    assert plan is not None
    first_step = plan.steps[0]
    assert first_step.args.get("identifier_type") == "manufacturer_name"


def test_planner_identifier_plan_infers_component_code_for_order_code_term() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(user_input="find order code FT-200")
    )

    assert plan is not None
    first_step = plan.steps[0]
    assert first_step.args.get("identifier_type") == "component_code"


def test_planner_simple_question_not_matched_as_identifier() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(user_input="what is the oil change interval")
    )

    assert plan is None


def test_planner_creates_explore_and_answer_plan() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(
            user_input="explore this document and list maintenance tasks",
            selected_document_id="doc-42",
            selected_document_title="FWC12 Manual",
        )
    )

    assert plan is not None
    assert plan.tool_names == ["explore_document", "answer_question"]
    assert plan.requires_document is True


def test_planner_creates_retrieve_and_answer_plan() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(
            user_input="retrieve evidence for oil change and summarize it",
            document_query="FWC12",
        )
    )

    assert plan is not None
    assert plan.tool_names == ["find_document", "retrieve_chunks", "answer_question"]
    assert plan.requires_document is True


def test_planner_creates_compare_plan() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(
            user_input="compare specifications and maintenance tasks",
            selected_document_id="doc-42",
        )
    )

    assert plan is not None
    assert plan.tool_names == [
        "answer_question",
        "answer_question",
        "format_combined_answer",
    ]


def test_planner_returns_none_for_simple_list_documents() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(user_input="list documents")
    )

    assert plan is None


def test_planner_returns_none_for_simple_question() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(user_input="what is the oil change interval")
    )

    assert plan is None


def test_planner_uses_selected_document_when_available() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(
            user_input="compare safety warnings and procedures",
            selected_document_id="doc-selected",
            selected_document_title="Pump Manual",
        )
    )

    assert plan is not None
    assert plan.document_id == "doc-selected"
    assert plan.document_title == "Pump Manual"


def test_planner_marks_document_required_for_document_scoped_plan() -> None:
    plan = DeterministicPlanner().create_plan(
        build_agent_state(user_input="compare safety warnings and procedures")
    )

    assert plan is not None
    assert plan.requires_document is True


# ---------------------------------------------------------------------------
# End-to-end: planner output passes PlanValidator
# ---------------------------------------------------------------------------

def test_identifier_query_produces_plan_with_correct_steps() -> None:
    state = build_agent_state(
        user_input="find part number HP-001",
        selected_document_id="doc-42",
    )
    plan = DeterministicPlanner().create_plan(state)

    assert plan is not None
    assert plan.tool_names[0] == "retrieve_identifiers"
    assert plan.tool_names[-1] == "answer_question"
    assert plan.diagnostics["plan_kind"] == "identifier_lookup"


def test_plan_validator_accepts_deterministic_identifier_plan() -> None:
    state = build_agent_state(
        user_input="find part number HP-001",
        selected_document_id="doc-42",
    )
    plan = DeterministicPlanner().create_plan(state)

    assert plan is not None

    result = PlanValidator().validate(
        plan,
        policy=PlanPolicy.default(),
        tool_registry=_full_tool_registry(),
        state=state,
    )

    assert result.success is True, result.errors
