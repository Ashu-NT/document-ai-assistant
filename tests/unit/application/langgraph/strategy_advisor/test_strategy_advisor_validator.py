from src.application.langgraph.retrieval_strategy.models import RetrievalStrategy
from src.application.langgraph.strategy_advisor import (
    StrategyAdvisorRequest,
    StrategyAdvisorValidator,
)
from src.shared.exceptions import SchemaValidationError


def test_strategy_advisor_validator_accepts_grounded_json_only_response() -> None:
    validator = StrategyAdvisorValidator()

    proposal = validator.validate_response(
        """
        {
          "intent": "comparison",
          "route": "deep_research",
          "confidence": 0.91,
          "concepts": ["troubleshooting", "maintenance", "procedures"],
          "recommended_strategies": [
            "TROUBLESHOOTING_LOOKUP",
            "MAINTENANCE_LOOKUP",
            "PROCEDURE_LOOKUP"
          ],
          "comparison": true,
          "requires_table": true,
          "reason": "The query compares multiple maintenance-related concepts."
        }
        """,
        request=StrategyAdvisorRequest(
            query_text="compare troubleshooting procedures and maintenance tasks",
            deterministic_route="answer_question",
            deterministic_route_confidence=0.70,
            deterministic_reason="Fell back to question answering.",
            deterministic_strategies=[RetrievalStrategy.MAINTENANCE_LOOKUP],
            allowed_routes=["answer_question", "deep_research"],
        ),
    )

    assert proposal.intent.value == "comparison"
    assert proposal.route == "deep_research"
    assert proposal.concepts == ["troubleshooting", "maintenance", "procedures"]
    assert proposal.recommended_strategies == [
        RetrievalStrategy.TROUBLESHOOTING_LOOKUP,
        RetrievalStrategy.MAINTENANCE_LOOKUP,
        RetrievalStrategy.PROCEDURE_LOOKUP,
    ]


def test_strategy_advisor_validator_rejects_ungrounded_or_hallucinated_fields() -> None:
    validator = StrategyAdvisorValidator()

    try:
        validator.validate_response(
            """
            {
              "intent": "comparison",
              "route": "deep_research",
              "confidence": 0.92,
              "concepts": ["scheduled servicing", "fault recovery"],
              "recommended_strategies": ["MAINTENANCE_LOOKUP"],
              "comparison": true,
              "requires_table": false,
              "reason": "The query compares two concepts.",
              "tools": ["retrieve_chunks"]
            }
            """,
            request=StrategyAdvisorRequest(
                query_text="compare troubleshooting procedures and maintenance tasks",
                deterministic_route="answer_question",
                deterministic_route_confidence=0.70,
                deterministic_reason="Fell back to question answering.",
                allowed_routes=["answer_question", "deep_research"],
            ),
        )
    except SchemaValidationError as exc:
        assert "unsupported keys" in exc.message.lower()
    else:  # pragma: no cover
        raise AssertionError("Expected strategy advisor validation to reject extra keys.")
