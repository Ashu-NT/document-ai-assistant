from __future__ import annotations

from typing import Any

from src.application.agent_runtime.bootstrap.agent_service_builder import AgentServices


def build_agent_node_factory(
    services: AgentServices,
    *,
    enable_llm_research_planning: bool,
) -> Any:
    from src.application.langgraph import (
        ClarificationBuilder,
        EvidenceMerger,
        LLMResearchPlanner,
        NodeFactory,
        ReflectionJsonParser,
        ReflectionPolicy,
        ReflectionService,
        ReflectionValidator,
        ResearchPolicy,
        RetryQueryBuilder,
        RetrievalRetryPolicy,
    )
    from src.application.langgraph.planning import (
        LLMPlanProposer,
        PlanParser,
        PlanPolicy,
        PlanRepair,
        PlanValidator,
    )
    from src.application.langgraph.retrieval_strategy import (
        RetrievalPlanExecutor,
        RetrievalStrategyPolicy,
        RetrievalStrategyService,
        StrategyRetryPolicy,
    )
    from src.application.prompts.reflection import ReflectionPromptBuilder
    from src.config.settings import langgraph_settings, llm_settings

    planning_llm_service = services.planning_llm_service
    retrieval_strategy_policy = RetrievalStrategyPolicy(
        enabled=langgraph_settings.retrieval_strategy_enabled,
        llm_strategy_enabled=langgraph_settings.llm_retrieval_strategy_enabled,
    )
    return NodeFactory(
        llm_plan_proposer=(
            LLMPlanProposer(
                planning_llm_service,
                model=llm_settings.planning_llm or llm_settings.general_llm,
            )
            if planning_llm_service is not None
            else None
        ),
        plan_parser=PlanParser(),
        plan_validator=PlanValidator(),
        plan_policy=PlanPolicy(max_steps=langgraph_settings.max_steps),
        plan_repair=PlanRepair(),
        reflection_service=ReflectionService(
            llm_service=services.reflection_llm_service,
            prompt_builder=ReflectionPromptBuilder(),
            json_parser=ReflectionJsonParser(),
            validator=ReflectionValidator(),
            policy=ReflectionPolicy(enabled=True),
            model=services.reflection_model,
        ),
        evidence_merger=EvidenceMerger(),
        retry_query_builder=RetryQueryBuilder(),
        clarification_builder=ClarificationBuilder(),
        retrieval_retry_policy=RetrievalRetryPolicy(),
        retrieval_strategy_service=RetrievalStrategyService(
            strategy_advisor=services.strategy_advisor,
            policy=retrieval_strategy_policy,
        ),
        retrieval_plan_executor=RetrievalPlanExecutor(),
        retrieval_strategy_policy=retrieval_strategy_policy,
        strategy_retry_policy=StrategyRetryPolicy(),
        strategy_advisor=services.strategy_advisor,
        llm_research_planner=(
            LLMResearchPlanner(
                planning_llm_service,
                model=llm_settings.planning_llm or llm_settings.general_llm,
            )
            if planning_llm_service is not None and enable_llm_research_planning
            else None
        ),
        research_policy=ResearchPolicy(
            enabled=langgraph_settings.deep_research_enabled,
            llm_research_planning_enabled=(
                langgraph_settings.llm_research_planning_enabled
            ),
        ),
    )
