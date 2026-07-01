from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.planning import PlanPolicy, PlanPromptBuilder
from src.application.langgraph.routing import RouteDecision, RouteType
from src.application.langgraph.state import build_agent_state


def test_plan_prompt_builder_includes_allowed_tools_and_json_rules() -> None:
    builder = PlanPromptBuilder()
    prompt = builder.build(
        user_input="Find the pressure transmitter document and summarize the specifications.",
        state=build_agent_state(
            user_input="Find the pressure transmitter document and summarize the specifications.",
            selected_document_id="doc-42",
            selected_document_title="Pump Manual",
        ),
        route_decision=RouteDecision(
            route_type=RouteType.PLANNED_TASK,
            confidence=0.82,
            reason="Compound request needs a plan.",
            extracted_question="Find the pressure transmitter document and summarize the specifications.",
            is_compound=True,
            requires_plan=True,
        ),
        tool_registry=ToolRegistry(
            find_document_tool=object(),
            answer_question_tool=object(),
            retrieve_chunks_tool=object(),
        ),
        policy=PlanPolicy.default(),
    )

    assert "Return JSON only." in prompt
    assert "find_document" in prompt
    assert "answer_question" in prompt
    assert "retrieve_chunks" in prompt
    assert "ingest_document" not in prompt
    assert "Selected document id: doc-42" in prompt
    assert "Selected document title: Pump Manual" in prompt


def test_plan_prompt_builder_includes_retrieve_identifiers_hint() -> None:
    builder = PlanPromptBuilder()
    prompt = builder.build(
        user_input="find part number HP-001",
        state=build_agent_state(user_input="find part number HP-001"),
        route_decision=RouteDecision(
            route_type=RouteType.PLANNED_TASK,
            confidence=0.9,
            reason="Identifier lookup.",
            extracted_question="find part number HP-001",
            is_compound=True,
            requires_plan=True,
        ),
        tool_registry=ToolRegistry(
            retrieve_identifiers_tool=object(),
            answer_question_tool=object(),
        ),
        policy=PlanPolicy.default(),
    )

    assert "retrieve_identifiers" in prompt
    assert "part_number" in prompt


def test_plan_prompt_builder_hint_describes_identifier_types() -> None:
    builder = PlanPromptBuilder()
    prompt = builder.build(
        user_input="find serial number SN-001",
        state=build_agent_state(user_input="find serial number SN-001"),
        route_decision=RouteDecision(
            route_type=RouteType.PLANNED_TASK,
            confidence=0.9,
            reason="Identifier lookup.",
            extracted_question="find serial number SN-001",
            is_compound=True,
            requires_plan=True,
        ),
        tool_registry=ToolRegistry(retrieve_identifiers_tool=object()),
        policy=PlanPolicy.default(),
    )

    assert "serial_number" in prompt
    assert "model_number" in prompt


def test_plan_prompt_builder_hint_uses_component_code_not_order_code() -> None:
    builder = PlanPromptBuilder()
    prompt = builder.build(
        user_input="find component code",
        state=build_agent_state(user_input="find component code"),
        route_decision=RouteDecision(
            route_type=RouteType.PLANNED_TASK,
            confidence=0.9,
            reason="Identifier lookup.",
            extracted_question="find component code",
            is_compound=True,
            requires_plan=True,
        ),
        tool_registry=ToolRegistry(retrieve_identifiers_tool=object()),
        policy=PlanPolicy.default(),
    )

    assert "component_code" in prompt
    assert "order_code" not in prompt


def test_plan_prompt_builder_hint_includes_certificate_number_and_manufacturer_name() -> None:
    builder = PlanPromptBuilder()
    prompt = builder.build(
        user_input="find certificate number ISO-9001",
        state=build_agent_state(user_input="find certificate number ISO-9001"),
        route_decision=RouteDecision(
            route_type=RouteType.PLANNED_TASK,
            confidence=0.9,
            reason="Identifier lookup.",
            extracted_question="find certificate number ISO-9001",
            is_compound=True,
            requires_plan=True,
        ),
        tool_registry=ToolRegistry(retrieve_identifiers_tool=object()),
        policy=PlanPolicy.default(),
    )

    assert "certificate_number" in prompt
    assert "manufacturer_name" in prompt


def test_plan_prompt_builder_includes_recent_history_summary() -> None:
    builder = PlanPromptBuilder()
    prompt = builder.build(
        user_input="Compare the maintenance and safety sections.",
        state=build_agent_state(
            user_input="Compare the maintenance and safety sections.",
            history=[
                {"role": "user", "content": "Open FWC12"},
                {"role": "assistant", "content": "Selected Pump Manual."},
            ],
        ),
        route_decision=RouteDecision(
            route_type=RouteType.PLANNED_TASK,
            confidence=0.9,
            reason="Compound request needs a plan.",
            extracted_question="Compare the maintenance and safety sections.",
            is_compound=True,
            requires_plan=True,
        ),
        tool_registry=ToolRegistry(answer_question_tool=object()),
        policy=PlanPolicy.default(),
    )

    assert "Recent conversation summary:" in prompt
    assert "user: Open FWC12" in prompt
