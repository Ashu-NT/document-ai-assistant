from src.application.langgraph.routing import IntentRouter, RouteType


def test_intent_router_routes_list_documents_command() -> None:
    decision = IntentRouter().route("list documents")

    assert decision.route_type == RouteType.LIST_DOCUMENTS


def test_intent_router_routes_unknown_question_to_answer_question() -> None:
    decision = IntentRouter().route("What is the maintenance interval?")

    assert decision.route_type == RouteType.ANSWER_QUESTION
    assert decision.extracted_question == "What is the maintenance interval?"


def test_intent_router_routes_explore_document_command() -> None:
    decision = IntentRouter().route("explore document Pump Manual")

    assert decision.route_type == RouteType.DOCUMENT_EXPLORATION
    assert decision.extracted_document_query == "pump manual"


def test_intent_router_routes_select_document_command() -> None:
    decision = IntentRouter().route("open FWC12")

    assert decision.route_type == RouteType.SELECT_DOCUMENT
    assert decision.extracted_document_query == "fwc12"


def test_intent_router_routes_current_document_command() -> None:
    decision = IntentRouter().route("current document")

    assert decision.route_type == RouteType.CURRENT_DOCUMENT


def test_intent_router_routes_clear_document_command() -> None:
    decision = IntentRouter().route("clear document")

    assert decision.route_type == RouteType.CLEAR_DOCUMENT


def test_intent_router_routes_numeric_clarification_response() -> None:
    decision = IntentRouter().route("1")

    assert decision.route_type == RouteType.CLARIFICATION_RESPONSE
    assert decision.clarification_candidate_index == 0


def test_intent_router_routes_help_and_exit_commands() -> None:
    help_decision = IntentRouter().route("help")
    exit_decision = IntentRouter().route("exit")

    assert help_decision.route_type == RouteType.HELP
    assert exit_decision.route_type == RouteType.EXIT


def test_intent_router_marks_explore_it_as_current_document_usage() -> None:
    decision = IntentRouter().route("explore it")

    assert decision.route_type == RouteType.DOCUMENT_EXPLORATION
    assert decision.uses_current_document is True


def test_intent_router_routes_compound_request_to_planned_task() -> None:
    decision = IntentRouter().route("compare specifications and maintenance tasks")

    assert decision.route_type == RouteType.PLANNED_TASK
    assert decision.is_compound is True
    assert decision.requires_plan is True


def test_intent_router_routes_retrieve_and_summarize_to_planned_task() -> None:
    decision = IntentRouter().route("retrieve evidence and summarize maintenance tasks")

    assert decision.route_type == RouteType.PLANNED_TASK
    assert decision.requires_plan is True


def test_intent_router_routes_unsafe_delete_request_to_blocked_action() -> None:
    decision = IntentRouter().route("delete all documents and reingest them")

    assert decision.route_type == RouteType.BLOCKED_ACTION
    assert decision.options["unsafe_request_blocked"] is True


def test_intent_router_routes_unsafe_retrieval_follow_up_to_blocked_action() -> None:
    decision = IntentRouter().route("delete all documents and retrieve evidence afterward")

    assert decision.route_type == RouteType.BLOCKED_ACTION
    assert decision.requires_plan is False


def test_intent_router_does_not_block_normal_delete_word_question() -> None:
    decision = IntentRouter().route("How do I delete an alarm from the device?")

    assert decision.route_type == RouteType.ANSWER_QUESTION
