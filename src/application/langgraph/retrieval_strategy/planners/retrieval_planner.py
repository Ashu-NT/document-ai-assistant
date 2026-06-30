from __future__ import annotations

from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.retrieval_strategy.models import (
    RetrievalPlan,
    RetrievalStrategyDecision,
)
from src.application.langgraph.retrieval_strategy.planners.retrieval_plan_builder import (
    RetrievalPlanBuilder,
)
from src.application.langgraph.retrieval_strategy.policies import (
    RetrievalStrategyPolicy,
)


class RetrievalPlanner:
    def __init__(
        self,
        *,
        plan_builder: RetrievalPlanBuilder | None = None,
    ) -> None:
        self.plan_builder = plan_builder or RetrievalPlanBuilder()

    def plan(
        self,
        decision: RetrievalStrategyDecision,
        *,
        tool_registry: ToolRegistry,
        policy: RetrievalStrategyPolicy,
    ) -> RetrievalPlan:
        return self.plan_builder.build(
            decision,
            tool_registry=tool_registry,
            policy=policy,
        )
