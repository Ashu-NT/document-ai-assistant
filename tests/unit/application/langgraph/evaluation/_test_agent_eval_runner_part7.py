from src.application.langgraph.common import GraphResult

from src.application.langgraph.evaluation import (
    AgentEvalRunner,
    AgentExpectedBehavior,
    AgentTestCase,
    AgentTurnInput,
)

class FakeGraph:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.selected_by_session: dict[str, tuple[str, str]] = {}

    def run(self, user_input: str, **kwargs):
        session_id = kwargs["session_id"]
        self.calls.append((user_input, dict(kwargs)))
        normalized = user_input.lower()

        if normalized == "open fwc12":
            self.selected_by_session[session_id] = ("doc-fwc12", "FWC12 Manual")
            return GraphResult.ok(
                response_text="Selected document: FWC12 Manual.",
                route="select_document",
                data={
                    "selected_document_id": "doc-fwc12",
                    "selected_document_title": "FWC12 Manual",
                    "selected_document_file_name": "19P006-31-FWC12-5-1-0_Manual.pdf",
                },
                diagnostics={"needs_clarification": False},
                trace=[
                    {
                        "node_name": "find_document",
                        "tool_name": "find_document",
                    }
                ],
            )

        if normalized == "open pressure":
            return GraphResult.ok(
                response_text="I found multiple matching documents.",
                route="select_document",
                data={
                    "pending_clarification": {"kind": "document_selection"},
                    "clarification_options": [
                        {
                            "document_id": "doc-pressure-1",
                            "display_name": "Pressure Transmitter",
                        }
                    ],
                },
                diagnostics={"needs_clarification": True},
                trace=[
                    {
                        "node_name": "find_document",
                        "tool_name": "find_document",
                    }
                ],
            )

        if normalized == "1":
            self.selected_by_session[session_id] = (
                "doc-pressure-1",
                "Pressure Transmitter",
            )
            return GraphResult.ok(
                response_text="Selected document: Pressure Transmitter.",
                route="clarification_response",
                data={
                    "selected_document_id": "doc-pressure-1",
                    "selected_document_title": "Pressure Transmitter",
                },
                diagnostics={"needs_clarification": False},
            )

        if normalized.startswith("what are the maintenance intervals"):
            document_id, title = self.selected_by_session[session_id]
            requested_strategy = kwargs.get("requested_retrieval_strategy")
            retrieval_strategy_primary = (
                "TABLE_LOOKUP"
                if requested_strategy == "table"
                else "MAINTENANCE_LOOKUP"
            )
            data = {
                "answer": "The interval is 500 hours.",
                "selected_document_id": document_id,
                "selected_document_title": title,
                "context_chunks": [
                    {"chunk_id": "chunk-1", "document_id": document_id}
                ],
            }
            if kwargs.get("retrieval_strategy_enabled"):
                data["retrieval_strategy_decision"] = {
                    "primary_strategy": retrieval_strategy_primary,
                    "secondary_strategies": ["TABLE_LOOKUP"]
                    if retrieval_strategy_primary == "MAINTENANCE_LOOKUP"
                    else [],
                }
                data["retrieval_strategy_trace"] = {
                    "signals": ["maintenance"],
                    "final_decision": {
                        "primary_strategy": retrieval_strategy_primary
                    },
                }
            return GraphResult.ok(
                response_text="The interval is 500 hours.",
                route="answer_question",
                data=data,
                diagnostics={"needs_clarification": False},
                trace=[
                    {
                        "node_name": "answer_question",
                        "tool_name": "answer_question",
                    }
                ],
            )

        if normalized.startswith("retrieve shaft seal lubrication"):
            document_id, title = self.selected_by_session[session_id]
            return GraphResult.ok(
                response_text="Retrieved supporting evidence.",
                route="retrieve_evidence",
                data={
                    "selected_document_id": document_id,
                    "selected_document_title": title,
                    "context_chunks": [
                        {"chunk_id": "chunk-2", "document_id": document_id}
                    ],
                },
                diagnostics={"needs_clarification": False},
                trace=[
                    {
                        "node_name": "retrieve_evidence",
                        "tool_name": "retrieve_chunks",
                    }
                ],
            )

        if normalized.startswith("compare specifications and maintenance tasks"):
            document_id, title = self.selected_by_session[session_id]
            return GraphResult.ok(
                response_text="Plan executed successfully.",
                route="planned_task",
                data={
                    "selected_document_id": document_id,
                    "selected_document_title": title,
                    "validated_plan": {
                        "plan_id": "plan-1",
                        "steps": [
                            {"tool_name": "answer_question"},
                            {"tool_name": "answer_question"},
                        ],
                    },
                    "plan_steps": [
                        {"tool_name": "answer_question"},
                        {"tool_name": "answer_question"},
                    ],
                    "planning_source": "deterministic",
                },
                trace=[
                    {
                        "node_name": "plan_step",
                        "tool_name": "answer_question",
                    }
                ],
            )

        if normalized.startswith("generate a preventive maintenance report"):
            document_id, title = self.selected_by_session[session_id]
            return GraphResult.ok(
                response_text=(
                    "# Research Report\n\n## Executive Summary\nMaintenance tasks and intervals were collected."
                ),
                route="deep_research",
                data={
                    "selected_document_id": document_id,
                    "selected_document_title": title,
                    "context_chunks": [
                        {"chunk_id": "chunk-r1", "document_id": document_id}
                    ],
                    "citations": [{"citation_id": "cit-r1"}],
                    "research_plan": {
                        "plan_id": "research-plan-1",
                        "tasks": [
                            {"task_id": "task-1", "title": "Collect maintenance tasks"},
                            {"task_id": "task-2", "title": "Collect maintenance intervals"},
                        ],
                    },
                    "research_task_results": [
                        {"task_id": "task-1", "success": True},
                        {"task_id": "task-2", "success": True},
                    ],
                    "research_gaps": [],
                    "research_report": {
                        "title": "Research Report",
                        "executive_summary": "Maintenance tasks and intervals were collected.",
                        "sections": [
                            {
                                "title": "Scheduled Tasks",
                                "body": "Lubrication and inspection tasks were found.",
                            }
                        ],
                    },
                    "research_trace": {"plan_source": "deterministic"},
                    "research_plan_source": "deterministic",
                },
                diagnostics={"needs_clarification": False},
                trace=[
                    {
                        "node_name": "execute_research",
                    }
                ],
            )

        if "delete all documents" in normalized:
            return GraphResult.ok(
                response_text="This request was blocked because it attempts to mutate the document corpus.",
                route="blocked_action",
                data={
                    "unsafe_request_blocked": True,
                    "blocked_reason": "Request attempts destructive corpus mutation.",
                    "blocked_terms": ["delete all documents"],
                },
                diagnostics={
                    "unsafe_request_blocked": True,
                    "blocked_reason": "Request attempts destructive corpus mutation.",
                },
                trace=[{"node_name": "create_plan"}],
            )

        return GraphResult.ok(response_text="Unhandled.", route="unknown")

def test_agent_eval_runner_tracks_deep_research_metrics() -> None:
    graph = FakeGraph()
    cases = [
        AgentTestCase(
            case_id="AG-009",
            name="Deep research report",
            description=None,
            inputs=[
                AgentTurnInput(user_input="open FWC12"),
                AgentTurnInput(
                    user_input="Generate a preventive maintenance report",
                    deep_research_enabled=True,
                    show_research_plan=True,
                    show_research_trace=True,
                ),
            ],
            expected=AgentExpectedBehavior(
                final_route="deep_research",
                selected_document_contains="FWC12",
                research_plan_required=True,
                research_report_required=True,
                research_citation_required=True,
                research_task_success_min_rate=1.0,
            ),
        )
    ]

    report = AgentEvalRunner(graph=graph).run_cases(cases)

    case_result = report.case_results[0]
    assert case_result.passed is True
    assert case_result.metrics["deep_research_route_accuracy"] == 1.0
    assert case_result.metrics["research_plan_validity_rate"] == 1.0
    assert case_result.metrics["research_task_success_rate"] == 1.0
    assert case_result.metrics["research_report_completeness_rate"] == 1.0
    assert case_result.metrics["research_citation_coverage_rate"] == 1.0
