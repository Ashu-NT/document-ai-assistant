from dataclasses import dataclass

from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.nodes.control import PlanSummaryNode
from src.application.langgraph.nodes.planning import CreatePlanNode, ExecutePlanNode
from src.application.langgraph.planning import (
    DeterministicPlanner,
    ExecutionPlan,
    LLMPlanProposer,
    PlanExecutor,
    PlanStep,
)
from src.application.langgraph.state import build_agent_state
from src.application.tools.common import ToolResult


@dataclass(slots=True)
class FakeQAResult:
    answer_text: str | None = None


class FakeAnswerQuestionTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return ToolResult.ok(data=FakeQAResult(answer_text="Generated answer."))


class FakeLLMService:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0

    def generate(self, prompt: str, model: str | None = None) -> str:
        self.calls += 1
        return self.response


def test_create_plan_node_writes_plan_to_state() -> None:
    node = CreatePlanNode(DeterministicPlanner())

    patch = node(
        build_agent_state(
            user_input="compare specifications and maintenance tasks",
            selected_document_id="doc-42",
        )
    )

    assert patch["execution_plan"]["goal"] == "compare specifications and maintenance tasks"
    assert len(patch["plan_steps"]) == 3
    assert patch["planning_source"] == "deterministic"


def test_create_plan_node_uses_llm_when_deterministic_plan_missing() -> None:
    class FakePlanner:
        def create_plan(self, state):
            return None

    llm_service = FakeLLMService(
        """
        {
          "goal": "Find and answer",
          "reason": "Need lookup first.",
          "steps": [
            {
              "step_id": "step_1",
              "tool_name": "find_document",
              "description": "Find the document",
              "args": {"query_text": "pump"},
              "output_key": "lookup",
              "depends_on": [],
              "required": true
            }
          ]
        }
        """
    )
    node = CreatePlanNode(
        FakePlanner(),
        tool_registry=ToolRegistry(find_document_tool=object()),
        llm_plan_proposer=LLMPlanProposer(llm_service),
    )
    state = build_agent_state(
        user_input="find the pump manual and summarize it",
        llm_planning_enabled=True,
    )
    state["route"] = "planned_task"

    patch = node(state)

    assert llm_service.calls == 1
    assert patch["execution_plan"]["goal"] == "Find and answer"
    assert patch["planning_source"] == "llm"
    assert patch["validated_plan"]["source"] == "llm"


def test_create_plan_node_does_not_call_llm_when_disabled() -> None:
    class FakePlanner:
        def create_plan(self, state):
            return None

    llm_service = FakeLLMService("{}")
    node = CreatePlanNode(
        FakePlanner(),
        tool_registry=ToolRegistry(find_document_tool=object()),
        llm_plan_proposer=LLMPlanProposer(llm_service),
    )
    state = build_agent_state(
        user_input="find the pump manual and summarize it",
        llm_planning_enabled=False,
    )
    state["route"] = "planned_task"

    patch = node(state)

    assert llm_service.calls == 0
    assert patch["route"] == "answer_question"
    assert patch["execution_plan"] is None


def test_create_plan_node_rejects_invalid_llm_plan() -> None:
    class FakePlanner:
        def create_plan(self, state):
            return None

    llm_service = FakeLLMService("not json")
    node = CreatePlanNode(
        FakePlanner(),
        tool_registry=ToolRegistry(find_document_tool=object()),
        llm_plan_proposer=LLMPlanProposer(llm_service),
    )
    state = build_agent_state(
        user_input="find the pump manual and summarize it",
        llm_planning_enabled=True,
        selected_document_id="doc-42",
    )
    state["route"] = "planned_task"

    patch = node(state)

    assert patch["execution_plan"] is None
    assert patch["planning_source"] == "failed"
    assert patch["planning_errors"]
    assert patch["error"]["error_code"] == "plan_validation_failed"


def test_execute_plan_node_writes_step_results_to_state() -> None:
    answer_tool = FakeAnswerQuestionTool()
    node = ExecutePlanNode(
        PlanExecutor(),
        ToolRegistry(answer_question_tool=answer_tool),
    )
    plan = ExecutionPlan(
        plan_id="plan_1",
        goal="answer",
        steps=[
            PlanStep(
                step_id="step_1",
                tool_name="answer_question",
                description="Answer the question.",
                output_key="answer",
                args={"question": "What is the maintenance interval?"},
            )
        ],
        reason="Single answer.",
    )
    state = build_agent_state(user_input="What is the maintenance interval?")
    state["execution_plan"] = plan.to_dict()

    patch = node(state)

    assert patch["plan_success"] is True
    assert patch["tool_results"]["answer"]["success"] is True
    assert answer_tool.requests[0].question == "What is the maintenance interval?"


def test_plan_summary_node_includes_plan_when_show_plan_enabled() -> None:
    patch = PlanSummaryNode()(
        build_agent_state(
            user_input="compare specifications and maintenance tasks",
            show_plan=True,
        )
        | {
            "execution_plan": {"plan_id": "plan_1", "goal": "compare"},
            "plan_steps": [
                {"description": "Answer specifications."},
                {"description": "Answer maintenance."},
            ],
            "response_text": "Specifications:\n...\n\nMaintenance:\n...",
        }
    )

    assert "Plan" in patch["response_text"]
    assert "1. Answer specifications." in patch["response_text"]
    assert "Answer" in patch["response_text"]


def test_plan_summary_node_hides_plan_when_show_plan_disabled() -> None:
    patch = PlanSummaryNode()(
        build_agent_state(
            user_input="compare specifications and maintenance tasks",
            show_plan=False,
        )
        | {
            "execution_plan": {"plan_id": "plan_1", "goal": "compare"},
            "plan_steps": [{"description": "Answer specifications."}],
            "response_text": "Specifications:\n...",
        }
    )

    assert patch["response_text"] == "Specifications:\n..."
