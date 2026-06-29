from __future__ import annotations

from typing import Any

from src.application.langgraph.memory import ConversationMemory
from src.application.langgraph.nodes import (
    AnswerQuestionNode,
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
from src.application.langgraph.planning import DeterministicPlanner, PlanExecutor
from src.application.langgraph.routing import IntentRouter
from src.application.langgraph.factories.tool_registry import ToolRegistry


class NodeFactory:
    def __init__(
        self,
        *,
        planner: DeterministicPlanner | None = None,
        plan_executor: PlanExecutor | None = None,
    ) -> None:
        self.planner = planner or DeterministicPlanner()
        self.plan_executor = plan_executor or PlanExecutor()

    def build_document_agent_nodes(
        self,
        *,
        tool_registry: ToolRegistry,
        intent_router: IntentRouter,
        memory: ConversationMemory | None,
    ) -> dict[str, Any]:
        return {
            "route_request": RouteRequestNode(intent_router),
            "create_plan": CreatePlanNode(self.planner),
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
