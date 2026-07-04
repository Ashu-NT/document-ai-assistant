from src.application.langgraph.retrieval_strategy.models import RetrievalStrategy
from src.application.langgraph.strategy_advisor import (
    StrategyAdvisor,
    StrategyAdvisorRequest,
    StrategyAdvisorStatus,
)


class FakeLLMService:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        *,
        response_schema: dict | None = None,
    ) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "response_schema": response_schema,
            }
        )
        return self.response


def test_strategy_advisor_passes_response_schema_and_accepts_valid_proposal() -> None:
    llm_service = FakeLLMService(
        '{"intent":"comparison","route":"deep_research","confidence":0.92,"concepts":["troubleshooting","maintenance","procedures"],"recommended_strategies":["TROUBLESHOOTING_LOOKUP","MAINTENANCE_LOOKUP","PROCEDURE_LOOKUP"],"comparison":true,"requires_table":false,"reason":"The query compares multiple maintenance-related concepts."}'
    )
    advisor = StrategyAdvisor(llm_service, model="advisor-model")

    outcome = advisor.advise(
        StrategyAdvisorRequest(
            query_text="compare troubleshooting procedures and maintenance tasks",
            deterministic_route="answer_question",
            deterministic_route_confidence=0.7,
            deterministic_reason="Fallback route.",
            deterministic_strategies=[RetrievalStrategy.MAINTENANCE_LOOKUP],
            allowed_routes=["answer_question", "deep_research"],
        )
    )

    assert outcome.status == StrategyAdvisorStatus.ACCEPTED
    assert outcome.proposal is not None
    assert outcome.proposal.route == "deep_research"
    assert llm_service.calls[0]["model"] == "advisor-model"
    assert isinstance(llm_service.calls[0]["response_schema"], dict)
