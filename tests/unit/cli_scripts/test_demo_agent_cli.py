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
