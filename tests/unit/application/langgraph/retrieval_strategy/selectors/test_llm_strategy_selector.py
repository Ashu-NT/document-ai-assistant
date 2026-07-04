from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategy,
)
from src.application.langgraph.retrieval_strategy.policies import (
    RetrievalStrategyPolicy,
)
from src.application.langgraph.retrieval_strategy.selectors.llm_strategy_selector import (
    LLMStrategySelector,
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


def test_llm_strategy_selector_passes_response_schema_and_marks_decision() -> None:
    llm_service = FakeLLMService(
        '{"primary_strategy":"IDENTIFIER_LOOKUP","secondary_strategies":["TABLE_LOOKUP"],"confidence":0.91,"reason":"Identifiers dominate the query.","rewritten_query":"part number","top_k":6}'
    )
    selector = LLMStrategySelector(llm_service, model="selector-model")

    decision = selector.select(
        context=RetrievalContext(query_text="find part number"),
        signals=[],
        policy=RetrievalStrategyPolicy(default_top_k=5, max_top_k=10),
    )

    assert decision.primary_strategy == RetrievalStrategy.IDENTIFIER_LOOKUP
    assert decision.secondary_strategies == [RetrievalStrategy.TABLE_LOOKUP]
    assert decision.use_llm_selector is True
    assert decision.diagnostics["selector"] == "llm"
    assert llm_service.calls[0]["model"] == "selector-model"
    assert isinstance(llm_service.calls[0]["response_schema"], dict)
