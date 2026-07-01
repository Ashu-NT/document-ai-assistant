from src.application.langgraph.nodes.control.route_request_node import RouteRequestNode
from src.application.langgraph.routing import RouteDecision, RouteType
from src.application.langgraph.state import build_agent_state
from src.application.langgraph.strategy_advisor import (
    StrategyAdvisorEvent,
    StrategyAdvisorIntent,
    StrategyAdvisorOutcome,
    StrategyAdvisorProposal,
    StrategyAdvisorStatus,
)


class _FakeIntentRouter:
    def route(self, user_input, *, document_id=None, document_query=None, deep_research_enabled=False):
        return RouteDecision(
            route_type=RouteType.ANSWER_QUESTION,
            confidence=0.70,
            reason="Fell back to question answering.",
            extracted_question=user_input,
        )


class _FakeStrategyAdvisor:
    def trigger_reason(self, request):
        return "low_deterministic_confidence"

    def advise(self, request):
        return StrategyAdvisorOutcome(
            status=StrategyAdvisorStatus.ACCEPTED,
            proposal=StrategyAdvisorProposal(
                intent=StrategyAdvisorIntent.COMPARISON,
                route=RouteType.DEEP_RESEARCH.value,
                confidence=0.93,
                concepts=["fault recovery", "scheduled servicing"],
                recommended_strategies=[],
                comparison=True,
                requires_table=False,
                reason="The request compares two maintenance-related concepts.",
            ),
            events=[
                StrategyAdvisorEvent(
                    name="StrategyAdvisorStarted",
                    message="started",
                ),
                StrategyAdvisorEvent(
                    name="StrategyAdvisorCompleted",
                    message="completed",
                ),
                StrategyAdvisorEvent(
                    name="StrategyValidated",
                    message="validated",
                ),
            ],
        )


def test_route_request_node_upgrades_answer_question_to_deep_research_from_guarded_advisor() -> None:
    node = RouteRequestNode(
        _FakeIntentRouter(),
        strategy_advisor=_FakeStrategyAdvisor(),
    )

    patch = node(
        build_agent_state(
            user_input="contrast fault recovery with scheduled servicing",
            deep_research_enabled=True,
            llm_retrieval_strategy_enabled=True,
        )
    )

    assert patch["route"] == RouteType.DEEP_RESEARCH.value
    assert patch["strategy_advisor_result"]["status"] == "accepted"
    assert any(
        event["name"] == "StrategyMerged"
        for event in patch["strategy_advisor_trace"]["events"]
    )
