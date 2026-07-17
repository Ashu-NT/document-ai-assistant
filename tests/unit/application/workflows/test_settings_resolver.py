from src.application.workflows.common.settings_resolver import resolve_setting


def test_resolve_setting_returns_loaded_value_without_callback() -> None:
    fallback_calls: list[int] = []

    result = resolve_setting(
        lambda: 42,
        7,
        on_fallback=fallback_calls.append,
    )

    assert result == 42
    assert fallback_calls == []


def test_resolve_setting_invokes_callback_when_loader_fails() -> None:
    fallback_calls: list[int] = []

    result = resolve_setting(
        lambda: 1 / 0,
        7,
        on_fallback=fallback_calls.append,
    )

    assert result == 7
    assert fallback_calls == [7]
