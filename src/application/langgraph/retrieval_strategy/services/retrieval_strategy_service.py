from __future__ import annotations

from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.retrieval_strategy.models.retrieval_context import (
    RetrievalContext,
)
from src.application.langgraph.retrieval_strategy.models.retrieval_strategy_decision import (
    RetrievalStrategyDecision,
)
from src.application.langgraph.retrieval_strategy.models.retrieval_strategy_result import (
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
from src.application.langgraph.strategy_advisor.advisor import StrategyAdvisor
from src.application.langgraph.strategy_advisor.advisor_models import (
    StrategyAdvisorOutcome,
    StrategyAdvisorRequest,
    StrategyAdvisorStatus,
)
from src.application.langgraph.strategy_advisor.strategy_merge import StrategyDecisionMerger
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
        strategy_advisor: StrategyAdvisor | None = None,
        strategy_validator: RetrievalStrategyValidator | None = None,
        planner: RetrievalPlanner | None = None,
        plan_validator: RetrievalPlanValidator | None = None,
        policy: RetrievalStrategyPolicy | None = None,
        decision_merger: StrategyDecisionMerger | None = None,
    ) -> None:
        self.query_analyzer = query_analyzer or RetrievalQueryAnalyzer()
        self.signal_extractor = signal_extractor or RetrievalSignalExtractor()
        self.deterministic_selector = (
            deterministic_selector or DeterministicStrategySelector()
        )
        self.llm_selector = llm_selector
        self.strategy_advisor = strategy_advisor
        self.strategy_validator = strategy_validator or RetrievalStrategyValidator()
        self.planner = planner or RetrievalPlanner()
        self.plan_validator = plan_validator or RetrievalPlanValidator()
        self.policy = policy or RetrievalStrategyPolicy()
        self.decision_merger = decision_merger or StrategyDecisionMerger()

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
        advisor_outcome = self._advisor_outcome(
            context=context,
            signals=signals,
            deterministic_decision=deterministic_decision,
        )
        advisor_proposal = (
            advisor_outcome.proposal
            if advisor_outcome is not None
            and advisor_outcome.status == StrategyAdvisorStatus.ACCEPTED
            else None
        )
        strategy_errors: list[str] = []
        if (
            advisor_outcome is not None
            and advisor_outcome.status == StrategyAdvisorStatus.REJECTED
            and advisor_outcome.reason
        ):
            strategy_errors.append(advisor_outcome.reason)
        if advisor_proposal is not None:
            final_decision = self.decision_merger.merge_retrieval_decision(
                deterministic_decision=deterministic_decision,
                proposal=advisor_proposal,
                query_text=context.query_text,
                policy=self.policy,
            )

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
        advisor_events = (
            [event.to_dict() for event in advisor_outcome.events]
            if advisor_outcome is not None
            else []
        )
        if advisor_proposal is not None:
            advisor_events.append(
                {
                    "name": "StrategyMerged",
                    "message": "Validated advisor strategies were merged with the deterministic baseline.",
                    "diagnostics": {
                        "selected_strategies": [
                            strategy.value
                            for strategy in validated_decision.selected_strategies
                        ]
                    },
                }
            )
        trace = RetrievalStrategyTrace(
            signals=serialize_graph_value(signals),
            deterministic_decision=serialize_graph_value(deterministic_decision),
            llm_decision=None,
            advisor_proposal=(
                serialize_graph_value(advisor_proposal.to_dict())
                if advisor_proposal is not None
                else None
            ),
            advisor_status=(
                advisor_outcome.status.value
                if advisor_outcome is not None
                else (
                    "accepted"
                    if context.strategy_advisor_proposal is not None
                    else None
                )
            ),
            advisor_events=serialize_graph_value(advisor_events),
            final_decision=serialize_graph_value(validated_decision),
            fallback_reason=(
                "validator_fallback"
                if validated_decision.primary_strategy != final_decision.primary_strategy
                else None
            ),
            plan_steps=serialize_graph_value([step.to_dict() for step in validated_plan.steps]),
            errors=strategy_errors,
        )
        return RetrievalStrategyResult(
            decision=validated_decision,
            plan=validated_plan,
            trace=trace,
            diagnostics={
                "trace_id": new_id("rst"),
                "advisor_status": trace.advisor_status,
                "strategy_errors": strategy_errors,
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

    def _advisor_outcome(
        self,
        *,
        context: RetrievalContext,
        signals,
        deterministic_decision: RetrievalStrategyDecision,
    ) -> StrategyAdvisorOutcome | None:
        if context.strategy_advisor_proposal is not None:
            return StrategyAdvisorOutcome(
                status=StrategyAdvisorStatus.ACCEPTED,
                proposal=context.strategy_advisor_proposal,
            )
        if (
            not self.policy.llm_strategy_enabled
            or not context.use_llm_selector
            or self.strategy_advisor is None
            or context.requested_strategy is not None
        ):
            return None
        request = StrategyAdvisorRequest(
            query_text=context.query_text,
            deterministic_route=context.route,
            deterministic_route_confidence=deterministic_decision.confidence,
            deterministic_reason=deterministic_decision.reason,
            deterministic_strategies=list(deterministic_decision.selected_strategies),
            signals=[
                f"{signal.category}:{signal.value}:{signal.score:.2f}"
                for signal in signals
            ],
            selected_document_id=context.effective_document_id,
            selected_document_title=context.effective_document_title,
            allowed_routes=[context.route] if context.route else [],
        )
        trigger_reason = self.strategy_advisor.trigger_reason(request)
        if trigger_reason is None:
            return None
        request.trigger_reason = trigger_reason
        return self.strategy_advisor.advise(request)
