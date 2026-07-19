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

def test_agent_cli_show_raw_plan_help_documents_its_trace_dependency(capsys) -> None:
    """finding F15: --show-raw-plan silently requires --trace (an explicit
    runtime error if missing) but --help didn't say so -- it must now."""
    mod = _load_script("agent_cli")

    try:
        mod.parse_args(["--help"])
    except SystemExit:
        pass

    help_output = capsys.readouterr().out
    show_raw_plan_index = help_output.index("--show-raw-plan")
    following_text = help_output[show_raw_plan_index : show_raw_plan_index + 200]
    assert "--trace" in following_text

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
    assert "[1] Maintenance Schedule | maintenance_interval" in output
    assert "Pump Manual (doc_12345678)" in output
    assert "6 Maintenance > Maintenance Schedule" in output
    assert "12-13" in output
    assert "0.9132" in output
    assert "Oil change interval is 500 hours." in output
    assert "Route:" not in output
    assert "Success:" not in output

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

    assert mod.console_safe_text("\uf0b7 item") == "? item"

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
