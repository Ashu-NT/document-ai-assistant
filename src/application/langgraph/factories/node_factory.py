from __future__ import annotations

from typing import Any

from src.application.langgraph.memory import ConversationMemory
from src.application.langgraph.nodes import (
    AnswerQuestionNode,
    BlockedActionNode,
    ClarifyRequestNode,
    CreatePlanNode,
    CreateResearchPlanNode,
    DocumentDetailsNode,
    ErrorHandlerNode,
    ExecutePlanNode,
    ExecuteResearchNode,
    EvaluateResearchNode,
    ExploreDocumentNode,
    FinalResponseNode,
    FindDocumentNode,
    ListDocumentsNode,
    OutOfScopeNode,
    PlanSummaryNode,
    ReflectAnswerNode,
    ResearchSummaryNode,
    RetrievalTraceNode,
    RetrieveEvidenceNode,
    RouteRequestNode,
    RetryRetrievalNode,
    RunQualityGateNode,
    SessionCommandNode,
    SynthesizeResearchNode,
)
from src.application.langgraph.retrieval_strategy import (
    RetrievalPlanExecutor,
    RetrievalStrategyPolicy,
    RetrievalStrategyService,
    StrategyRetryPolicy,
)
from src.application.langgraph.research import (
    LLMResearchPlanner,
    ResearchExecutor,
    ResearchPolicy,
    ResearchService,
    ResearchTaskExecutor,
)
from src.application.langgraph.reflection import (
    ClarificationBuilder,
    EvidenceMerger,
    ReflectionService,
    RetryQueryBuilder,
    RetrievalRetryPolicy,
)
from src.application.langgraph.planning import (
    DeterministicPlanner,
    LLMPlanProposer,
    PlanExecutor,
    PlanParser,
    PlanPolicy,
    PlanRepair,
    PlanValidator,
)
from src.application.langgraph.routing import IntentRouter
from src.application.langgraph.factories.tool_registry import ToolRegistry


class NodeFactory:
    def __init__(
        self,
        *,
        planner: DeterministicPlanner | None = None,
        plan_executor: PlanExecutor | None = None,
        llm_plan_proposer: LLMPlanProposer | None = None,
        plan_parser: PlanParser | None = None,
        plan_validator: PlanValidator | None = None,
        plan_policy: PlanPolicy | None = None,
        plan_repair: PlanRepair | None = None,
        reflection_service: ReflectionService | None = None,
        evidence_merger: EvidenceMerger | None = None,
        retry_query_builder: RetryQueryBuilder | None = None,
        clarification_builder: ClarificationBuilder | None = None,
        retrieval_retry_policy: RetrievalRetryPolicy | None = None,
        retrieval_strategy_service: RetrievalStrategyService | None = None,
        retrieval_plan_executor: RetrievalPlanExecutor | None = None,
        retrieval_strategy_policy: RetrievalStrategyPolicy | None = None,
        strategy_retry_policy: StrategyRetryPolicy | None = None,
        research_service: ResearchService | None = None,
        llm_research_planner: LLMResearchPlanner | None = None,
        research_policy: ResearchPolicy | None = None,
    ) -> None:
        self.planner = planner or DeterministicPlanner()
        self.plan_executor = plan_executor or PlanExecutor()
        self.llm_plan_proposer = llm_plan_proposer
        self.plan_parser = plan_parser or PlanParser()
        self.plan_validator = plan_validator or PlanValidator()
        self.plan_policy = plan_policy or PlanPolicy.default()
        self.plan_repair = plan_repair or PlanRepair()
        self.reflection_service = reflection_service
        self.evidence_merger = evidence_merger or EvidenceMerger()
        self.retry_query_builder = retry_query_builder or RetryQueryBuilder()
        self.clarification_builder = clarification_builder or ClarificationBuilder()
        self.retrieval_retry_policy = (
            retrieval_retry_policy or RetrievalRetryPolicy()
        )
        self.retrieval_strategy_service = (
            retrieval_strategy_service or RetrievalStrategyService()
        )
        self.retrieval_plan_executor = (
            retrieval_plan_executor or RetrievalPlanExecutor()
        )
        self.retrieval_strategy_policy = (
            retrieval_strategy_policy or RetrievalStrategyPolicy()
        )
        self.strategy_retry_policy = strategy_retry_policy or StrategyRetryPolicy()
        self.llm_research_planner = llm_research_planner
        self.research_policy = research_policy or ResearchPolicy()
        self.research_service = research_service or ResearchService(
            llm_planner=self.llm_research_planner,
            executor=ResearchExecutor(
                task_executor=ResearchTaskExecutor(
                    retrieval_strategy_service=self.retrieval_strategy_service,
                    retrieval_plan_executor=self.retrieval_plan_executor,
                )
            ),
            policy=self.research_policy,
        )

    def build_document_agent_nodes(
        self,
        *,
        tool_registry: ToolRegistry,
        intent_router: IntentRouter,
        memory: ConversationMemory | None,
    ) -> dict[str, Any]:
        return {
            "route_request": RouteRequestNode(intent_router),
            "blocked_action": BlockedActionNode(),
            "out_of_scope": OutOfScopeNode(),
            "create_plan": CreatePlanNode(
                self.planner,
                tool_registry=tool_registry,
                llm_plan_proposer=self.llm_plan_proposer,
                plan_parser=self.plan_parser,
                plan_validator=self.plan_validator,
                plan_policy=self.plan_policy,
                plan_repair=self.plan_repair,
            ),
            "execute_plan": ExecutePlanNode(self.plan_executor, tool_registry),
            "create_research_plan": CreateResearchPlanNode(self.research_service),
            "execute_research": ExecuteResearchNode(
                self.research_service,
                tool_registry,
            ),
            "evaluate_research": EvaluateResearchNode(self.research_service),
            "synthesize_research": SynthesizeResearchNode(self.research_service),
            "research_summary": ResearchSummaryNode(self.research_service),
            "list_documents": ListDocumentsNode(tool_registry),
            "find_document": FindDocumentNode(tool_registry),
            "document_details": DocumentDetailsNode(tool_registry),
            "explore_document": ExploreDocumentNode(tool_registry),
            "retrieve_evidence": RetrieveEvidenceNode(
                tool_registry,
                retrieval_strategy_service=self.retrieval_strategy_service,
                retrieval_plan_executor=self.retrieval_plan_executor,
                retrieval_strategy_policy=self.retrieval_strategy_policy,
            ),
            "answer_question": AnswerQuestionNode(
                tool_registry,
                retrieval_strategy_service=self.retrieval_strategy_service,
                retrieval_plan_executor=self.retrieval_plan_executor,
                retrieval_strategy_policy=self.retrieval_strategy_policy,
            ),
            "reflect_answer": ReflectAnswerNode(
                tool_registry,
                reflection_service=self.reflection_service,
                clarification_builder=self.clarification_builder,
            ),
            "retry_retrieval": RetryRetrievalNode(
                tool_registry,
                evidence_merger=self.evidence_merger,
                retry_query_builder=self.retry_query_builder,
                retry_policy=self.retrieval_retry_policy,
                retrieval_strategy_service=self.retrieval_strategy_service,
                retrieval_plan_executor=self.retrieval_plan_executor,
                retrieval_strategy_policy=self.retrieval_strategy_policy,
                strategy_retry_policy=self.strategy_retry_policy,
            ),
            "run_quality_gate": RunQualityGateNode(tool_registry),
            "retrieval_trace": RetrievalTraceNode(tool_registry),
            "clarify_request": ClarifyRequestNode(),
            "error_handler": ErrorHandlerNode(),
            "session_command": SessionCommandNode(),
            "plan_summary": PlanSummaryNode(),
            "final_response": FinalResponseNode(memory=memory),
        }
