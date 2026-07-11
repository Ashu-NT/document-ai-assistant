from tests.unit.cli_scripts.test_cli_scripts import _load_script

from src.application.langgraph.common import GraphResult

def test_agent_cli_show_retrieval_strategy_falls_back_to_research_tasks(capsys) -> None:
    mod = _load_script("agent_cli")
    result = GraphResult.ok(
        response_text="Comparison Summary\n\nProfessional answer.",
        route="deep_research",
        data={
            "answer": "Comparison Summary\n\nProfessional answer.",
            "research_plan": {
                "tasks": [
                    {
                        "task_id": "task-1",
                        "title": "Collect maintenance tasks",
                        "strategy_hint": "MAINTENANCE_LOOKUP",
                    },
                    {
                        "task_id": "task-2",
                        "title": "Collect technical specifications",
                        "strategy_hint": "TECHNICAL_SPECIFICATION",
                    },
                ]
            },
            "research_trace": {
                "retrieval_strategies_per_task": {
                    "task-1": "MAINTENANCE_LOOKUP",
                    "task-2": "TECHNICAL_SPECIFICATION",
                }
            },
        },
    )

    mod.print_graph_result(
        result,
        show_context=False,
        show_trace=False,
        show_retrieval_strategy=True,
    )

    output = capsys.readouterr().out
    assert "Task: Collect maintenance tasks" in output
    assert "Primary: MAINTENANCE_LOOKUP" in output
    assert "Secondary: TABLE_LOOKUP" in output
    assert "Task: Collect technical specifications" in output
    assert "Primary: TECHNICAL_SPECIFICATION" in output
    assert "No retrieval strategy decision was recorded." not in output

def test_agent_cli_show_research_outputs_plan_and_trace(capsys) -> None:
    mod = _load_script("agent_cli")
    result = GraphResult.ok(
        response_text="# Research Report\n\n## Executive Summary\nSummary text.",
        route="deep_research",
        data={
            "answer": "# Research Report\n\n## Executive Summary\nSummary text.",
            "research_plan": {
                "tasks": [
                    {
                        "title": "Collect maintenance tasks",
                        "strategy_hint": "MAINTENANCE_LOOKUP",
                    }
                ]
            },
            "research_trace": {
                "plan_source": "deterministic",
                "evidence_counts_per_task": {"task_1": 2},
                "gaps": [],
            },
        },
    )

    mod.print_graph_result(
        result,
        show_context=False,
        show_trace=False,
        show_research_plan=True,
        show_research_trace=True,
    )

    output = capsys.readouterr().out
    assert "Research Plan" in output
    assert "Collect maintenance tasks (MAINTENANCE_LOOKUP)" in output
    assert "Research Trace" in output
    assert "Plan source: deterministic" in output
    assert "task_1: 2" in output

def test_agent_cli_parse_args_supports_debug_flag() -> None:
    mod = _load_script("agent_cli")

    args = mod.parse_args(["What is the oil change interval?", "--debug"])

    assert args.debug is True

def test_agent_cli_build_json_output_includes_trace_only_when_requested() -> None:
    mod = _load_script("agent_cli")
    result = GraphResult.ok(
        response_text="The interval is 500 hours.",
        route="answer_question",
        data={
            "document_id": "doc_123",
            "selected_document_id": "doc_123",
            "selected_document_title": "Pump Manual",
            "pending_clarification": None,
            "clarification_options": [],
            "should_exit": False,
            "answer": "The interval is 500 hours.",
            "answer_intent": "maintenance_summary",
            "retrieval_strategy_decision": {
                "primary_strategy": "MAINTENANCE_LOOKUP"
            },
            "retrieval_plan": {"steps": [{"tool_name": "retrieve_chunks"}]},
            "retrieval_execution_result": {"success": True},
            "retrieval_strategy_trace": {"signals": []},
            "selected_retrieval_strategies": ["MAINTENANCE_LOOKUP"],
            "retrieval_strategy_errors": [],
            "context_chunks": [{"chunk_id": "chunk_1"}],
            "citations": [{"citation_id": "cit_1"}],
            "execution_plan": {"plan_id": "plan_1"},
            "validated_plan": {"plan_id": "plan_1", "source": "llm"},
            "plan_steps": [{"description": "Answer the question."}],
            "plan_results": {"plan_success": True},
            "plan_success": True,
            "failed_plan_step": None,
            "planning_source": "llm",
            "planning_errors": [],
            "planning_warnings": ["Repaired unsupported arg."],
            "raw_llm_plan": '{"goal":"Answer"}',
        },
        diagnostics={"needs_clarification": False},
        trace=[{"node_name": "answer_question"}],
    )

    without_trace = mod.build_json_output(result, include_trace=False)
    with_trace = mod.build_json_output(result, include_trace=True)

    assert without_trace["route"] == "answer_question"
    assert without_trace["success"] is True
    assert without_trace["answer"] == "The interval is 500 hours."
    assert without_trace["answer_intent"] == "maintenance_summary"
    assert without_trace["document_id"] == "doc_123"
    assert without_trace["selected_document_id"] == "doc_123"
    assert without_trace["selected_document_title"] == "Pump Manual"
    assert without_trace["retrieval_strategy_decision"] == {
        "primary_strategy": "MAINTENANCE_LOOKUP"
    }
    assert without_trace["retrieval_plan"] == {"steps": [{"tool_name": "retrieve_chunks"}]}
    assert without_trace["retrieval_execution_result"] == {"success": True}
    assert without_trace["selected_retrieval_strategies"] == ["MAINTENANCE_LOOKUP"]
    assert without_trace["clarification_options"] == []
    assert without_trace["context_chunks"] == [{"chunk_id": "chunk_1"}]
    assert without_trace["citations"] == [{"citation_id": "cit_1"}]
    assert without_trace["execution_plan"] == {"plan_id": "plan_1"}
    assert without_trace["validated_plan"] == {"plan_id": "plan_1", "source": "llm"}
    assert without_trace["plan_steps"] == [{"description": "Answer the question."}]
    assert without_trace["plan_results"] == {"plan_success": True}
    assert without_trace["plan_success"] is True
    assert without_trace["failed_plan_step"] is None
    assert without_trace["planning_source"] == "llm"
    assert without_trace["planning_warnings"] == ["Repaired unsupported arg."]
    assert "trace" not in without_trace
    assert "raw_llm_plan" not in without_trace
    assert with_trace["trace"] == [{"node_name": "answer_question"}]
    assert with_trace["raw_llm_plan"] == '{"goal":"Answer"}'

def test_agent_cli_show_plan_output_includes_plan_text(capsys) -> None:
    mod = _load_script("agent_cli")
    result = GraphResult.ok(
        response_text=(
            "Plan\n----\n1. Retrieve evidence chunks.\n2. Summarize the result.\n\n"
            "Answer\n------\nThe interval is 500 hours."
        ),
        route="planned_task",
        data={
            "execution_plan": {"plan_id": "plan_1"},
            "plan_steps": [{"description": "Retrieve evidence chunks."}],
        },
    )

    mod.print_graph_result(
        result,
        show_plan=True,
        show_context=False,
        show_trace=False,
    )

    output = capsys.readouterr().out
    assert "Plan" in output
    assert "Retrieve evidence chunks." in output

def test_agent_cli_show_raw_plan_output_requires_data(capsys) -> None:
    mod = _load_script("agent_cli")
    result = GraphResult.ok(
        response_text="Answer text.",
        route="planned_task",
        data={"raw_llm_plan": '{"goal":"Answer"}'},
    )

    mod.print_graph_result(
        result,
        show_plan=False,
        show_raw_plan=True,
        show_context=False,
        show_trace=False,
    )

    output = capsys.readouterr().out
    assert "Raw Plan" in output
    assert '{"goal":"Answer"}' in output

def test_agent_cli_interactive_loop_exits_on_exit_command(monkeypatch, capsys) -> None:
    mod = _load_script("agent_cli")

    class FakeGraph:
        def __init__(self) -> None:
            self.calls = []

        def run(self, user_input, **kwargs):
            self.calls.append((user_input, kwargs))
            return GraphResult.ok(
                response_text="Exiting document agent.",
                route="exit",
                data={"should_exit": True},
            )

    fake_runtime = mod.AgentRuntime(graph=FakeGraph())
    monkeypatch.setattr("builtins.input", lambda _: "exit")

    exit_code = mod.run_interactive_loop(
        fake_runtime,
        session_id="demo",
        initial_user_input=None,
        document_id=None,
        document_query=None,
        allow_answer_generation=False,
        include_context=False,
        llm_planning_enabled=False,
        top_k=None,
        emit_json=False,
        show_raw_plan=False,
        show_trace=False,
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Interactive session started: demo" in output
    assert "Exiting document agent." in output

def test_agent_cli_print_graph_result_shows_debug_metadata_only_when_requested(capsys) -> None:
    mod = _load_script("agent_cli")
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={"answer": "Answer text."},
    )

    mod.print_graph_result(
        result,
        show_debug=True,
        show_context=False,
        show_trace=False,
    )

    output = capsys.readouterr().out
    assert "Route: answer_question" in output
    assert "Success: True" in output
