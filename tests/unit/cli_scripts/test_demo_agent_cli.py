from tests.unit.cli_scripts.test_cli_scripts import _load_script


def test_demo_agent_cli_module_importable() -> None:
    mod = _load_script("demo_agent_cli")

    assert hasattr(mod, "parse_args")
    assert hasattr(mod, "main")


def test_demo_agent_cli_starts_interactive_when_no_question_is_passed() -> None:
    mod = _load_script("demo_agent_cli")

    args = mod.parse_args([])

    assert mod.should_start_interactive(args) is True


def test_demo_agent_cli_respects_quiet() -> None:
    mod = _load_script("demo_agent_cli")

    args = mod.parse_args(["--quiet"])

    assert args.quiet is True


def test_demo_agent_cli_parses_interactive_runtime_flags() -> None:
    mod = _load_script("demo_agent_cli")

    args = mod.parse_args(
        [
            "What is the drive specification?",
            "--document",
            "FWC12",
            "--show-react",
            "--deep-research",
            "--reflection",
            "--llm-planning",
            "--retrieval-strategy",
            "--write-trace",
            "--debug",
        ]
    )

    assert args.document == "FWC12"
    assert args.show_react is True
    assert args.deep_research is True
    assert args.reflection is True
    assert args.llm_planning is True
    assert args.retrieval_strategy is True
    assert args.write_trace is True
    assert args.debug is True


def test_demo_agent_cli_suppresses_post_run_trace_in_normal_show_react_mode() -> None:
    mod = _load_script("demo_agent_cli")

    class _Presenter:
        def __init__(self) -> None:
            self.show_react = None

        def render_graph_result(self, **kwargs):
            self.show_react = kwargs["show_react"]
            return "rendered"

        def render_command_result(self, *args, **kwargs):
            return "command"

    class _Handled:
        command_result = None
        export_paths = None

        def __init__(self) -> None:
            self.graph_result = object()
            self.react_trace = object()

    class _RuntimeOptions:
        debug = False
        write_trace = False

    class _Session:
        runtime_options = _RuntimeOptions()
        conversation_history = type("_History", (), {"turns": []})()

    presenter = _Presenter()
    mod._print_handled_result(
        _Handled(),
        presenter=presenter,
        session=_Session(),
        show_react=True,
        policy=object(),
    )

    assert presenter.show_react is False


def test_demo_agent_cli_allows_post_run_trace_in_debug_mode() -> None:
    mod = _load_script("demo_agent_cli")

    class _Presenter:
        def __init__(self) -> None:
            self.show_react = None

        def render_graph_result(self, **kwargs):
            self.show_react = kwargs["show_react"]
            return "rendered"

        def render_command_result(self, *args, **kwargs):
            return "command"

    class _Handled:
        command_result = None
        export_paths = None

        def __init__(self) -> None:
            self.graph_result = object()
            self.react_trace = object()

    class _RuntimeOptions:
        debug = True
        write_trace = False

    class _Session:
        runtime_options = _RuntimeOptions()
        conversation_history = type("_History", (), {"turns": []})()

    presenter = _Presenter()
    mod._print_handled_result(
        _Handled(),
        presenter=presenter,
        session=_Session(),
        show_react=True,
        policy=object(),
    )

    assert presenter.show_react is True
