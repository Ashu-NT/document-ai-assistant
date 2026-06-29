from __future__ import annotations

from typing import Any

from src.application.langgraph.memory import ConversationMemory
from src.application.langgraph.nodes import (
    AnswerQuestionNode,
    BlockedActionNode,
    ClarifyRequestNode,
    CreatePlanNode,
    DocumentDetailsNode,
    ErrorHandlerNode,
    ExecutePlanNode,
    ExploreDocumentNode,
    FinalResponseNode,
    FindDocumentNode,
    ListDocumentsNode,
    PlanSummaryNode,
    RetrievalTraceNode,
    RetrieveEvidenceNode,
    RouteRequestNode,
    RunQualityGateNode,
    SessionCommandNode,
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
    ) -> None:
        self.planner = planner or DeterministicPlanner()
        self.plan_executor = plan_executor or PlanExecutor()
        self.llm_plan_proposer = llm_plan_proposer
        self.plan_parser = plan_parser or PlanParser()
        self.plan_validator = plan_validator or PlanValidator()
        self.plan_policy = plan_policy or PlanPolicy.default()
        self.plan_repair = plan_repair or PlanRepair()

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
            "list_documents": ListDocumentsNode(tool_registry),
            "find_document": FindDocumentNode(tool_registry),
            "document_details": DocumentDetailsNode(tool_registry),
            "explore_document": ExploreDocumentNode(tool_registry),
            "retrieve_evidence": RetrieveEvidenceNode(tool_registry),
            "answer_question": AnswerQuestionNode(tool_registry),
            "run_quality_gate": RunQualityGateNode(tool_registry),
            "retrieval_trace": RetrievalTraceNode(tool_registry),
            "clarify_request": ClarifyRequestNode(),
            "error_handler": ErrorHandlerNode(),
            "session_command": SessionCommandNode(),
            "plan_summary": PlanSummaryNode(),
            "final_response": FinalResponseNode(memory=memory),
        }
