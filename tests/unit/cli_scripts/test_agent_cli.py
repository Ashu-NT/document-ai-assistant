from tests.unit.cli_scripts.test_cli_scripts import _load_script

from src.application.langgraph.common import GraphResult


def test_agent_cli_module_importable() -> None:
    mod = _load_script("agent_cli")

    assert hasattr(mod, "parse_args")
    assert hasattr(mod, "main")


def test_agent_cli_parses_basic_arguments() -> None:
    mod = _load_script("agent_cli")

    args = mod.parse_args(
        [
            "retrieve shaft seal lubrication",
            "--session-id",
            "demo",
            "--document",
            "FWC12",
            "--top-k",
            "7",
            "--show-context",
            "--show-plan",
            "--llm-planning",
            "--json",
        ]
    )

    assert args.user_input == "retrieve shaft seal lubrication"
    assert args.session_id == "demo"
    assert args.document == "FWC12"
    assert args.top_k == 7
    assert args.show_context is True
    assert args.show_plan is True
    assert args.llm_planning is True
    assert args.json is True


def test_agent_cli_parses_interactive_flag() -> None:
    mod = _load_script("agent_cli")

    args = mod.parse_args(["--interactive", "--session-id", "demo"])

    assert args.interactive is True
    assert args.session_id == "demo"


def test_agent_cli_parses_raw_plan_flags() -> None:
    mod = _load_script("agent_cli")

    args = mod.parse_args(["question", "--llm-planning", "--show-raw-plan", "--trace"])

    assert args.llm_planning is True
    assert args.show_raw_plan is True
    assert args.trace is True


def test_agent_cli_parses_reflection_flags() -> None:
    mod = _load_script("agent_cli")

    args = mod.parse_args(["question", "--reflection", "--show-reflection"])

    assert args.reflection is True
    assert args.show_reflection is True


def test_agent_cli_parses_deep_research_flags() -> None:
    mod = _load_script("agent_cli")

    args = mod.parse_args(
        [
            "question",
            "--deep-research",
            "--llm-research-planning",
            "--show-research-plan",
            "--show-research-trace",
        ]
    )

    assert args.deep_research is True
    assert args.llm_research_planning is True
    assert args.show_research_plan is True
    assert args.show_research_trace is True


def test_agent_cli_parses_retrieval_strategy_flags() -> None:
    mod = _load_script("agent_cli")

    args = mod.parse_args(
        [
            "question",
            "--retrieval-strategy",
            "table",
            "--llm-retrieval-strategy",
            "--show-retrieval-strategy",
        ]
    )

    assert args.retrieval_strategy == "table"
    assert args.llm_retrieval_strategy is True
    assert args.show_retrieval_strategy is True


def test_agent_cli_show_context_prints_context_chunks(capsys) -> None:
    mod = _load_script("agent_cli")
    result = GraphResult.ok(
        response_text="The interval is 500 hours.",
        route="answer_question",
        data={
            "document_id": "doc_1234567890abcdef",
            "answer": "The interval is 500 hours.",
            "answer_intent": "maintenance_summary",
            "context_chunks": [
                {
                    "chunk_id": "chunk_001",
                    "document_id": "doc_1234567890abcdef",
                    "document_title": "Pump Manual",
                    "chunk_type": "maintenance_interval",
                    "section_title": "Maintenance Schedule",
                    "section_path": ["6 Maintenance", "Maintenance Schedule"],
                    "source": {"page_start": 12, "page_end": 13},
                    "score": 0.9132,
                    "content": "Oil change interval is 500 hours. Lubricate bearings every 250 hours.",
                }
            ],
            "citations": [],
        },
    )

    mod.print_graph_result(
        result,
        show_context=True,
        show_trace=False,
    )

    output = capsys.readouterr().out
    assert "Context Chunks" in output
    assert "Answer intent: maintenance_summary" in output
    assert "[1] Maintenance Schedule | maintenance_interval" in output
    assert "Pump Manual (doc_12345678)" in output
    assert "6 Maintenance > Maintenance Schedule" in output
    assert "12-13" in output
    assert "0.9132" in output
    assert "Oil change interval is 500 hours." in output


def test_agent_cli_print_graph_result_prefers_payload_answer(capsys) -> None:
    mod = _load_script("agent_cli")
    result = GraphResult.ok(
        response_text="Fallback response.",
        route="deep_research",
        data={
            "answer": "# Comparison Summary\n\nPreferred research answer.",
        },
    )

    mod.print_graph_result(
        result,
        show_context=False,
        show_trace=False,
    )

    output = capsys.readouterr().out
    assert "Preferred research answer." in output
    assert "Fallback response." not in output


def test_agent_cli_console_safe_text_replaces_unencodable_chars(monkeypatch) -> None:
    mod = _load_script("agent_cli")

    class _Stdout:
        encoding = "cp1252"

    monkeypatch.setattr(mod.sys, "stdout", _Stdout())

    assert mod._console_safe_text("\uf0b7 item") == "? item"


def test_agent_cli_show_reflection_prints_reflection_details(capsys) -> None:
    mod = _load_script("agent_cli")
    result = GraphResult.ok(
        response_text="The maintenance interval is 500 hours.",
        route="answer_question",
        data={
            "answer": "The maintenance interval is 500 hours.",
            "reflection_score": 0.83,
            "merged_chunk_ids": ["chunk_1", "chunk_2"],
            "reflection_result": {
                "decision": {
                    "decision": "RETRIEVE_AGAIN",
                    "reason": "The answer is missing the service-interval context.",
                    "retry_query": "maintenance interval service schedule operating hours",
                },
                "answer_quality_score": 0.62,
                "evidence_quality_score": 0.74,
            },
        },
    )

    mod.print_graph_result(
        result,
        show_context=False,
        show_trace=False,
        show_reflection=True,
    )

    output = capsys.readouterr().out
    assert "Reflection" in output
    assert "Decision: RETRIEVE_AGAIN" in output
    assert "Retry query: maintenance interval service schedule operating hours" in output
    assert "Merged chunks: 2" in output


def test_agent_cli_show_retrieval_strategy_prints_decision_and_plan(capsys) -> None:
    mod = _load_script("agent_cli")
    result = GraphResult.ok(
        response_text="The maintenance interval is 500 hours.",
        route="answer_question",
        data={
            "answer": "The maintenance interval is 500 hours.",
            "retrieval_strategy_decision": {
                "primary_strategy": "MAINTENANCE_LOOKUP",
                "secondary_strategies": ["TABLE_LOOKUP"],
                "confidence": 0.91,
                "reason": "Maintenance and schedule signals were detected.",
            },
            "retrieval_plan": {
                "steps": [
                    {
                        "tool_name": "retrieve_chunks",
                        "query": "maintenance interval schedule table",
                    }
                ]
            },
            "retrieval_strategy_errors": [],
        },
    )

    mod.print_graph_result(
        result,
        show_context=False,
        show_trace=False,
        show_retrieval_strategy=True,
    )

    output = capsys.readouterr().out
    assert "Retrieval Strategy" in output
    assert "Primary: MAINTENANCE_LOOKUP" in output
    assert "Secondary: TABLE_LOOKUP" in output
    assert "retrieve_chunks - maintenance interval schedule table" in output


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
