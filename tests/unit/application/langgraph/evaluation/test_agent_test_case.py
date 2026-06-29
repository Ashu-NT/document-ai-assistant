from src.application.langgraph.evaluation import (
    AgentExpectedBehavior,
    AgentTestCase,
    AgentTurnInput,
)


def test_agent_test_case_supports_multi_turn_defaults() -> None:
    case = AgentTestCase(
        case_id="AG-001",
        name="Multi-turn case",
        description=None,
        inputs=[
            AgentTurnInput(user_input="open FWC12"),
            AgentTurnInput(user_input="what are the maintenance intervals?"),
        ],
        expected=AgentExpectedBehavior(),
        tags=["memory"],
    )

    assert case.turn_count == 2
    assert case.has_tag("memory") is True
    assert case.expected.required_tools == []
    assert case.expected.forbidden_tools == []
    assert case.expected.answer_must_contain == []
