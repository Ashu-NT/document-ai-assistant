from tests.unit.application.langgraph.graphs._test_document_agent_graph_support import *  # noqa: F401,F403

def test_document_agent_graph_executes_validated_llm_plan() -> None:
    class FakePlanner:
        def create_plan(self, state):
            return None

    class FakePlannedIntentRouter:
        def route(self, user_input, *, document_id=None, document_query=None):
            return RouteDecision(
                route_type=RouteType.PLANNED_TASK,
                confidence=0.6,
                reason="Forced planned route.",
                extracted_question=user_input,
                is_compound=True,
                requires_plan=True,
            )

    llm_service = FakeLLMService(
        """
        {
          "goal": "Find and answer",
          "reason": "Resolve the document before answering.",
          "steps": [
            {
              "step_id": "step_1",
              "tool_name": "find_document",
              "description": "Find the document",
              "args": {"query_text": "FWC12"},
              "output_key": "lookup",
              "depends_on": [],
              "required": true
            },
            {
              "step_id": "step_2",
              "tool_name": "answer_question",
              "description": "Answer the question",
              "args": {"question": "What is the maintenance interval?"},
              "output_key": "answer",
              "depends_on": ["step_1"],
              "required": true
            }
          ]
        }
        """
    )
    answer_tool = FakeAnswerQuestionTool()
    router = FakePlannedIntentRouter()
    registry = ToolRegistry(
        find_document_tool=FakeFindDocumentTool(),
        answer_question_tool=answer_tool,
    )
    nodes = NodeFactory(
        planner=FakePlanner(),
        llm_plan_proposer=LLMPlanProposer(llm_service),
    ).build_document_agent_nodes(
        tool_registry=registry,
        intent_router=router,
        memory=None,
    )
    graph = DocumentAgentGraph(
        registry,
        intent_router=router,
        nodes=nodes,
    )

    result = graph.run(
        "find the best answer",
        llm_planning_enabled=True,
    )

    assert result.success is True
    assert result.route == "planned_task"
    assert result.data["planning_source"] == "llm"
    assert llm_service.calls == 1
    assert answer_tool.requests

def test_document_agent_graph_executes_repaired_llm_plan() -> None:
    """The LLM plan below uses tool_name "ask_question", which does not
    exist — PlanValidator must reject it (unknown tool, unsupported args),
    then PlanRepair renames it to "answer_question" and the repaired plan
    must pass validation and execute for real through the graph. This is
    the repair branch of CreatePlanNode._attempt_llm_plan, which the
    existing "executes_validated_llm_plan" test never reaches because its
    fixture plan is already valid on the first pass."""

    class FakePlanner:
        def create_plan(self, state):
            return None

    class FakePlannedIntentRouter:
        def route(self, user_input, *, document_id=None, document_query=None):
            return RouteDecision(
                route_type=RouteType.PLANNED_TASK,
                confidence=0.6,
                reason="Forced planned route.",
                extracted_question=user_input,
                is_compound=True,
                requires_plan=True,
            )

    llm_service = FakeLLMService(
        """
        {
          "goal": "Find and answer",
          "reason": "Resolve the document before answering.",
          "steps": [
            {
              "step_id": "step_1",
              "tool_name": "find_document",
              "description": "Find the document",
              "args": {"query_text": "FWC12"},
              "output_key": "lookup",
              "depends_on": [],
              "required": true
            },
            {
              "step_id": "step_2",
              "tool_name": "ask_question",
              "description": "Answer the question",
              "args": {"question": "What is the maintenance interval?"},
              "output_key": "answer",
              "depends_on": ["step_1"],
              "required": true
            }
          ]
        }
        """
    )
    answer_tool = FakeAnswerQuestionTool()
    router = FakePlannedIntentRouter()
    registry = ToolRegistry(
        find_document_tool=FakeFindDocumentTool(),
        answer_question_tool=answer_tool,
    )
    nodes = NodeFactory(
        planner=FakePlanner(),
        llm_plan_proposer=LLMPlanProposer(llm_service),
    ).build_document_agent_nodes(
        tool_registry=registry,
        intent_router=router,
        memory=None,
    )
    graph = DocumentAgentGraph(
        registry,
        intent_router=router,
        nodes=nodes,
    )

    result = graph.run(
        "find the best answer",
        llm_planning_enabled=True,
    )

    assert result.success is True
    assert result.route == "planned_task"
    assert result.data["planning_source"] == "repaired"
    assert any(
        "Renamed tool 'ask_question' to 'answer_question'" in warning
        for warning in result.data["planning_warnings"]
    )
    assert answer_tool.requests
    assert answer_tool.requests[0].question == "What is the maintenance interval?"
