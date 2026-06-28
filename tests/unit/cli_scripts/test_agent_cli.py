from tests.unit.cli_scripts.test_cli_scripts import _load_script


def test_agent_cli_module_importable() -> None:
    mod = _load_script("agent_cli")

    assert hasattr(mod, "parse_args")
    assert hasattr(mod, "main")


def test_agent_cli_parses_basic_arguments() -> None:
    mod = _load_script("agent_cli")

    args = mod.parse_args(
        [
            "retrieve shaft seal lubrication",
            "--document",
            "FWC12",
            "--top-k",
            "7",
            "--show-context",
            "--json",
        ]
    )

    assert args.user_input == "retrieve shaft seal lubrication"
    assert args.document == "FWC12"
    assert args.top_k == 7
    assert args.show_context is True
    assert args.json is True
