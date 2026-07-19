from src.config.settings.prompt_context_settings import PromptContextSettings


def test_prompt_context_settings_defaults() -> None:
    settings = PromptContextSettings()

    assert settings.max_items_per_array == 20
    assert settings.include_source_table_rows is False
    assert settings.max_table_rows_per_source == 20
    assert settings.max_rows_per_table == 20


def test_prompt_context_settings_max_items_per_array_overridable_via_env(
    monkeypatch,
) -> None:
    monkeypatch.setenv("PROMPT_CONTEXT_MAX_ITEMS_PER_ARRAY", "5")

    settings = PromptContextSettings()

    assert settings.max_items_per_array == 5


def test_prompt_context_settings_include_source_table_rows_overridable_via_env(
    monkeypatch,
) -> None:
    monkeypatch.setenv("PROMPT_CONTEXT_INCLUDE_SOURCE_TABLE_ROWS", "true")

    settings = PromptContextSettings()

    assert settings.include_source_table_rows is True


def test_prompt_context_settings_max_table_rows_per_source_overridable_via_env(
    monkeypatch,
) -> None:
    monkeypatch.setenv("PROMPT_CONTEXT_MAX_TABLE_ROWS_PER_SOURCE", "7")

    settings = PromptContextSettings()

    assert settings.max_table_rows_per_source == 7


def test_prompt_context_settings_max_rows_per_table_overridable_via_env(
    monkeypatch,
) -> None:
    monkeypatch.setenv("PROMPT_CONTEXT_MAX_ROWS_PER_TABLE", "3")

    settings = PromptContextSettings()

    assert settings.max_rows_per_table == 3
