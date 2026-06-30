from src.application.agent_runtime.demo_agent_runtime import DemoRuntimeStatus
from src.application.agent_runtime.presenters import StartupBanner


def test_banner_includes_title() -> None:
    banner = StartupBanner().render(
        runtime_status=DemoRuntimeStatus(document_count=23, model_name="qwen3:8b"),
        selected_document_name=None,
        quiet=False,
        no_examples=False,
    )

    assert "Document AI Agent" in banner


def test_banner_respects_quiet() -> None:
    banner = StartupBanner().render(
        runtime_status=DemoRuntimeStatus(),
        selected_document_name=None,
        quiet=True,
        no_examples=False,
    )

    assert banner == ""


def test_banner_respects_no_examples() -> None:
    banner = StartupBanner().render(
        runtime_status=DemoRuntimeStatus(),
        selected_document_name=None,
        quiet=False,
        no_examples=True,
    )

    assert "Try asking:" not in banner


def test_banner_includes_selected_document() -> None:
    banner = StartupBanner().render(
        runtime_status=DemoRuntimeStatus(),
        selected_document_name="FWC12 Manual",
        quiet=False,
        no_examples=False,
    )

    assert "Selected Doc    : FWC12 Manual" in banner
