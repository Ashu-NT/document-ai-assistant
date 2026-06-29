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
            "--json",
        ]
    )

    assert args.user_input == "retrieve shaft seal lubrication"
    assert args.session_id == "demo"
    assert args.document == "FWC12"
    assert args.top_k == 7
    assert args.show_context is True
    assert args.json is True


def test_agent_cli_parses_interactive_flag() -> None:
    mod = _load_script("agent_cli")

    args = mod.parse_args(["--interactive", "--session-id", "demo"])

    assert args.interactive is True
    assert args.session_id == "demo"


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
            "context_chunks": [{"chunk_id": "chunk_1"}],
            "citations": [{"citation_id": "cit_1"}],
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
    assert without_trace["clarification_options"] == []
    assert without_trace["context_chunks"] == [{"chunk_id": "chunk_1"}]
    assert without_trace["citations"] == [{"citation_id": "cit_1"}]
    assert "trace" not in without_trace
    assert with_trace["trace"] == [{"node_name": "answer_question"}]


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
        top_k=None,
        emit_json=False,
        show_trace=False,
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Interactive session started: demo" in output
    assert "Exiting document agent." in output
