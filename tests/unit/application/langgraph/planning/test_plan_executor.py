from dataclasses import dataclass

from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.planning import ExecutionPlan, PlanExecutor, PlanStep
from src.application.langgraph.state import build_agent_state
from src.application.tools.common import ToolResult


@dataclass(slots=True)
class FakeQAResult:
    answer_text: str | None = None


class RecordingTool:
    def __init__(self, result: ToolResult, log: list[str], name: str) -> None:
        self.result = result
        self.log = log
        self.name = name
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        self.log.append(self.name)
        return self.result


def test_plan_executor_executes_steps_in_order() -> None:
    call_log: list[str] = []
    list_tool = RecordingTool(
        ToolResult.ok(data=[{"document_id": "doc-42"}], message="Listed."),
        call_log,
        "list_documents",
    )
    find_tool = RecordingTool(
        ToolResult.ok(
            data={
                "document_id": "doc-42",
                "display_name": "Pump Manual",
                "file_name": "pump_manual.pdf",
            }
        ),
        call_log,
        "find_document",
    )
    answer_tool = RecordingTool(
        ToolResult.ok(data=FakeQAResult(answer_text="The interval is 500 hours.")),
        call_log,
        "answer_question",
    )
    registry = ToolRegistry(
        list_documents_tool=list_tool,
        find_document_tool=find_tool,
        answer_question_tool=answer_tool,
    )
    plan = ExecutionPlan(
        plan_id="plan_1",
        goal="show documents and open pressure transmitter",
        steps=[
            PlanStep(
                step_id="step_1",
                tool_name="list_documents",
                description="List documents.",
                output_key="listed_documents",
            ),
            PlanStep(
                step_id="step_2",
                tool_name="find_document",
                description="Find the document.",
                output_key="resolved_document",
                args={"query_text": "pressure transmitter"},
                depends_on=["listed_documents"],
            ),
            PlanStep(
                step_id="step_3",
                tool_name="answer_question",
                description="Answer the question.",
                output_key="answer",
                args={"question": "What is the maintenance interval?"},
                depends_on=["resolved_document"],
            ),
        ],
        reason="Compound request.",
    )

    state = build_agent_state(user_input="show documents and open pressure transmitter")
    next_state = PlanExecutor().execute(plan, state, registry)

    assert call_log == ["list_documents", "find_document", "answer_question"]
    assert next_state["plan_success"] is True
    assert next_state["response_text"] == "The interval is 500 hours."


def test_plan_executor_stops_on_required_step_failure() -> None:
    call_log: list[str] = []
    list_tool = RecordingTool(
        ToolResult.fail("Listing failed.", error_code="listing_failed"),
        call_log,
        "list_documents",
    )
    answer_tool = RecordingTool(
        ToolResult.ok(data=FakeQAResult(answer_text="Should not run.")),
        call_log,
        "answer_question",
    )
    registry = ToolRegistry(
        list_documents_tool=list_tool,
        answer_question_tool=answer_tool,
    )
    plan = ExecutionPlan(
        plan_id="plan_1",
        goal="broken plan",
        steps=[
            PlanStep(
                step_id="step_1",
                tool_name="list_documents",
                description="List documents.",
                output_key="listed_documents",
            ),
            PlanStep(
                step_id="step_2",
                tool_name="answer_question",
                description="Answer the question.",
                output_key="answer",
                depends_on=["listed_documents"],
            ),
        ],
        reason="Failure test.",
    )

    next_state = PlanExecutor().execute(
        plan,
        build_agent_state(user_input="show documents and answer"),
        registry,
    )

    assert call_log == ["list_documents"]
    assert next_state["plan_success"] is False
    assert next_state["failed_plan_step"] == "step_1"
    assert next_state["error"]["error_code"] == "listing_failed"


def test_plan_executor_stores_outputs_by_output_key() -> None:
    answer_tool = RecordingTool(
        ToolResult.ok(data=FakeQAResult(answer_text="Generated answer.")),
        [],
        "answer_question",
    )
    registry = ToolRegistry(answer_question_tool=answer_tool)
    plan = ExecutionPlan(
        plan_id="plan_1",
        goal="answer",
        steps=[
            PlanStep(
                step_id="step_1",
                tool_name="answer_question",
                description="Answer the question.",
                output_key="custom_answer",
                args={"question": "What is the maintenance interval?"},
            )
        ],
        reason="Answer test.",
    )

    next_state = PlanExecutor().execute(
        plan,
        build_agent_state(user_input="What is the maintenance interval?"),
        registry,
    )

    assert next_state["tool_results"]["custom_answer"]["success"] is True
    assert next_state["plan_results"]["step_outputs"]["custom_answer"]["success"] is True


def test_plan_executor_can_run_internal_formatting_without_external_tool() -> None:
    plan = ExecutionPlan(
        plan_id="plan_1",
        goal="compare",
        steps=[
            PlanStep(
                step_id="step_1",
                tool_name="format_combined_answer",
                description="Combine the answers.",
                output_key="combined_answer",
                args={"section_labels": ["Specifications", "Maintenance"]},
                depends_on=[],
            )
        ],
        reason="Formatting test.",
    )

    next_state = PlanExecutor().execute(
        plan,
        build_agent_state(user_input="compare specifications and maintenance tasks"),
        ToolRegistry(),
    )

    assert next_state["plan_success"] is True
    assert next_state["tool_results"]["combined_answer"]["success"] is True
