from __future__ import annotations

from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategyDecision,
    RetrievalStrategySignal,
)
from src.application.langgraph.retrieval_strategy.policies import (
    RetrievalStrategyPolicy,
)
from src.application.langgraph.retrieval_strategy.prompts import (
    RetrievalStrategyPromptBuilder,
)
from src.application.langgraph.retrieval_strategy.services.retrieval_strategy_json_parser import (
    RetrievalStrategyJsonParser,
)
from src.application.services.ai import LLMService


class LLMStrategySelector:
    def __init__(
        self,
        llm_service: LLMService,
        *,
        prompt_builder: RetrievalStrategyPromptBuilder | None = None,
        json_parser: RetrievalStrategyJsonParser | None = None,
        model: str | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.prompt_builder = prompt_builder or RetrievalStrategyPromptBuilder()
        self.json_parser = json_parser or RetrievalStrategyJsonParser()
        self.model = model

    def select(
        self,
        *,
        context: RetrievalContext,
        signals: list[RetrievalStrategySignal],
        policy: RetrievalStrategyPolicy,
    ) -> RetrievalStrategyDecision:
        prompt = self.prompt_builder.build(
            context=context,
            signals=signals,
            policy=policy,
        )
        response = self.llm_service.generate(prompt, model=self.model)
        decision = self.json_parser.parse(
            response,
            context=context,
            default_top_k=min(context.top_k or policy.default_top_k, policy.max_top_k),
        )
        decision.use_llm_selector = True
        decision.diagnostics.setdefault("selector", "llm")
        return decision
