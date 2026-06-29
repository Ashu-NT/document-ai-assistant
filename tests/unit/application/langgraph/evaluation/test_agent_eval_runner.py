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
            return GraphResult.ok(
                response_text="The interval is 500 hours.",
                route="answer_question",
                data={
                    "answer": "The interval is 500 hours.",
                    "selected_document_id": document_id,
                    "selected_document_title": title,
                    "context_chunks": [
                        {"chunk_id": "chunk-1", "document_id": document_id}
                    ],
                },
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

        if "delete all documents" in normalized:
            return GraphResult.fail(
                response_text="I could not build a safe multi-step plan for that request.",
                route="planned_task",
                error_code="plan_validation_failed",
                data={"planning_errors": ["Unsafe tool request."]},
                diagnostics={"planning_errors": ["Unsafe tool request."]},
                trace=[{"node_name": "create_plan"}],
            )

        return GraphResult.ok(response_text="Unhandled.", route="unknown")


def test_agent_eval_runner_runs_multi_turn_cases_with_session_memory() -> None:
    graph = FakeGraph()
    cases = [
        AgentTestCase(
            case_id="AG-001",
            name="Follow-up question",
            description=None,
            inputs=[
                AgentTurnInput(user_input="open FWC12"),
                AgentTurnInput(user_input="what are the maintenance intervals?"),
            ],
            expected=AgentExpectedBehavior(
                final_route="answer_question",
                selected_document_contains="FWC12",
                required_tools=["find_document", "answer_question"],
                success=True,
            ),
        )
    ]

    report = AgentEvalRunner(graph=graph).run_cases(cases)

    assert report.summary is not None
    assert report.summary.case_count == 1
    assert report.summary.route_accuracy == 1.0
    assert report.case_results[0].passed is True
    assert len({call[1]["session_id"] for call in graph.calls}) == 1


def test_agent_eval_runner_isolates_sessions_between_cases() -> None:
    graph = FakeGraph()
    cases = [
        AgentTestCase(
            case_id="AG-001",
            name="Case A",
            description=None,
            inputs=[
                AgentTurnInput(user_input="open FWC12"),
                AgentTurnInput(user_input="what are the maintenance intervals?"),
            ],
            expected=AgentExpectedBehavior(selected_document_contains="FWC12"),
        ),
        AgentTestCase(
            case_id="AG-002",
            name="Case B",
            description=None,
            inputs=[
                AgentTurnInput(user_input="open FWC12"),
                AgentTurnInput(user_input="retrieve shaft seal lubrication"),
            ],
            expected=AgentExpectedBehavior(
                final_route="retrieve_evidence",
                selected_document_contains="FWC12",
            ),
        ),
    ]

    report = AgentEvalRunner(graph=graph).run_cases(cases)

    session_ids = [call[1]["session_id"] for call in graph.calls if "session_id" in call[1]]
    assert len(set(session_ids)) == 2
    assert report.summary.case_count == 2


def test_agent_eval_runner_checks_clarification_plan_tools_and_scope() -> None:
    graph = FakeGraph()
    cases = [
        AgentTestCase(
            case_id="AG-003",
            name="Clarification",
            description=None,
            inputs=[AgentTurnInput(user_input="open pressure")],
            expected=AgentExpectedBehavior(
                final_route="select_document",
                should_clarify=True,
                required_tools=["find_document"],
                success=True,
            ),
        ),
        AgentTestCase(
            case_id="AG-004",
            name="Plan",
            description=None,
            inputs=[
                AgentTurnInput(user_input="open FWC12"),
                AgentTurnInput(
                    user_input="compare specifications and maintenance tasks",
                    show_plan=True,
                ),
            ],
            expected=AgentExpectedBehavior(
                final_route="planned_task",
                selected_document_contains="FWC12",
                required_plan_tools=["answer_question"],
            ),
        ),
        AgentTestCase(
            case_id="AG-005",
            name="Scope",
            description=None,
            inputs=[
                AgentTurnInput(user_input="open FWC12"),
                AgentTurnInput(
                    user_input="retrieve shaft seal lubrication",
                    show_context=True,
                ),
            ],
            expected=AgentExpectedBehavior(
                final_route="retrieve_evidence",
                context_document_id="doc-fwc12",
                required_tools=["retrieve_chunks"],
            ),
        ),
    ]

    report = AgentEvalRunner(graph=graph).run_cases(cases)

    assert all(case_result.passed for case_result in report.case_results)
    assert report.summary.clarification_accuracy == 1.0
    assert report.summary.plan_validity_rate == 1.0
    assert report.summary.document_scope_safety_rate == 1.0


def test_agent_eval_runner_checks_unsafe_request_blocking() -> None:
    graph = FakeGraph()
    cases = [
        AgentTestCase(
            case_id="AG-006",
            name="Unsafe request",
            description=None,
            inputs=[
                AgentTurnInput(
                    user_input="delete all documents and reingest them",
                    llm_planning_enabled=True,
                    show_plan=True,
                )
            ],
            expected=AgentExpectedBehavior(
                final_route="planned_task",
                unsafe_request_blocked=True,
                forbidden_tools=["delete_document", "ingest_document"],
            ),
        )
    ]

    report = AgentEvalRunner(graph=graph).run_cases(cases)

    assert report.case_results[0].passed is True
    assert report.summary.unsafe_block_rate == 1.0
