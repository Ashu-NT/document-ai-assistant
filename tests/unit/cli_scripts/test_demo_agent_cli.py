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


def test_build_visibility_policy_reveals_internal_ids_only_in_debug_mode() -> None:
    mod = _load_script("demo_agent_cli")

    default_args = mod.parse_args(["question"])
    debug_args = mod.parse_args(["question", "--debug"])

    default_policy = mod._build_visibility_policy(default_args)
    debug_policy = mod._build_visibility_policy(debug_args)

    assert default_policy.debug is False
    assert default_policy.show_internal_ids is False
    assert debug_policy.debug is True
    assert debug_policy.show_internal_ids is True


def test_demo_agent_cli_show_react_alone_triggers_post_run_trace() -> None:
    """finding 6.8: --show-react alone must be sufficient to render the
    post-run trace -- it previously silently required --debug or
    --write-trace as well. debug/write_trace no longer gate this at all."""
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

    assert presenter.show_react is True


def test_demo_agent_cli_show_react_help_documents_its_effect(capsys) -> None:
    """finding 6.8: --show-react previously had no help text at all -- its
    --help output must now explain what it does."""
    mod = _load_script("demo_agent_cli")

    try:
        mod.parse_args(["--help"])
    except SystemExit:
        pass

    help_output = capsys.readouterr().out
    show_react_index = help_output.index("--show-react")
    # The help text for --show-react is the text between its own entry and
    # the next "--" option in argparse's rendered help block.
    following_text = help_output[show_react_index : show_react_index + 200]
    assert "trace" in following_text.lower()



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
