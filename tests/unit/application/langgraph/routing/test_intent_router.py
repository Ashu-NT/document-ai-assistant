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
