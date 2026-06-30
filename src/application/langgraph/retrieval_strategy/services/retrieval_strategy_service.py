from __future__ import annotations

from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategyDecision,
    RetrievalStrategyResult,
)
from src.application.langgraph.retrieval_strategy.policies import (
    RetrievalStrategyPolicy,
)
from src.application.langgraph.retrieval_strategy.selectors import (
    DeterministicStrategySelector,
    LLMStrategySelector,
)
from src.application.langgraph.retrieval_strategy.planners import RetrievalPlanner
from src.application.langgraph.retrieval_strategy.services.retrieval_signal_extractor import (
    RetrievalSignalExtractor,
)
from src.application.langgraph.retrieval_strategy.tracing import RetrievalStrategyTrace
from src.application.langgraph.retrieval_strategy.validation import (
    RetrievalPlanValidator,
    RetrievalStrategyValidator,
)
from src.application.workflows.retrieval import RetrievalQueryAnalyzer
from src.domain.common import new_id
from src.domain.retrieval import RetrievalQuery


class RetrievalStrategyService:
    def __init__(
        self,
        *,
        query_analyzer: RetrievalQueryAnalyzer | None = None,
        signal_extractor: RetrievalSignalExtractor | None = None,
        deterministic_selector: DeterministicStrategySelector | None = None,
        llm_selector: LLMStrategySelector | None = None,
        strategy_validator: RetrievalStrategyValidator | None = None,
        planner: RetrievalPlanner | None = None,
        plan_validator: RetrievalPlanValidator | None = None,
        policy: RetrievalStrategyPolicy | None = None,
    ) -> None:
        self.query_analyzer = query_analyzer or RetrievalQueryAnalyzer()
        self.signal_extractor = signal_extractor or RetrievalSignalExtractor()
        self.deterministic_selector = (
            deterministic_selector or DeterministicStrategySelector()
        )
        self.llm_selector = llm_selector
        self.strategy_validator = strategy_validator or RetrievalStrategyValidator()
        self.planner = planner or RetrievalPlanner()
        self.plan_validator = plan_validator or RetrievalPlanValidator()
        self.policy = policy or RetrievalStrategyPolicy()

    def select_and_plan(
        self,
        context: RetrievalContext,
        *,
        tool_registry: ToolRegistry,
    ) -> RetrievalStrategyResult:
        analyzed_query = self._analyze_query(context)
        context.analyzed_query = analyzed_query
        signals = self.signal_extractor.extract(context)
        deterministic_decision = self.deterministic_selector.select(
            context=context,
            signals=signals,
            policy=self.policy,
        )

        final_decision = deterministic_decision
        llm_decision: RetrievalStrategyDecision | None = None
        llm_errors: list[str] = []
        if (
            self.policy.llm_strategy_enabled
            and context.use_llm_selector
            and self.llm_selector is not None
            and context.requested_strategy is None
        ):
            try:
                llm_decision = self.llm_selector.select(
                    context=context,
                    signals=signals,
                    policy=self.policy,
                )
                final_decision = llm_decision
            except Exception as exc:
                llm_errors.append(str(exc))

        validated_decision = self.strategy_validator.validate(
            final_decision,
            context=context,
            policy=self.policy,
        )
        plan = self.planner.plan(
            validated_decision,
            tool_registry=tool_registry,
            policy=self.policy,
        )
        validated_plan = self.plan_validator.validate(
            plan,
            tool_registry=tool_registry,
            policy=self.policy,
        )
        trace = RetrievalStrategyTrace(
            signals=serialize_graph_value(signals),
            deterministic_decision=serialize_graph_value(deterministic_decision),
            llm_decision=serialize_graph_value(llm_decision)
            if llm_decision is not None
            else None,
            final_decision=serialize_graph_value(validated_decision),
            fallback_reason=(
                "validator_fallback"
                if validated_decision.primary_strategy != final_decision.primary_strategy
                else None
            ),
            plan_steps=serialize_graph_value([step.to_dict() for step in validated_plan.steps]),
            errors=llm_errors,
        )
        return RetrievalStrategyResult(
            decision=validated_decision,
            plan=validated_plan,
            trace=trace,
            diagnostics={
                "trace_id": new_id("rst"),
                "llm_errors": llm_errors,
            },
        )

    def _analyze_query(self, context: RetrievalContext) -> RetrievalQuery:
        raw_query = RetrievalQuery(
            query_id=new_id("q"),
            query_text=context.retry_query or context.query_text,
            document_id=context.effective_document_id,
            top_k=context.top_k or self.policy.default_top_k,
        )
        return self.query_analyzer.analyze(raw_query)
