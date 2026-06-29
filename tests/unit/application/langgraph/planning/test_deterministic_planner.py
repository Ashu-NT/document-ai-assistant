from src.application.langgraph.planning import DeterministicPlanner
from src.application.langgraph.state import build_agent_state


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
