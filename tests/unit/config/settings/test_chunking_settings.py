from src.config.settings.chunking_settings import ChunkingSettings

# Every alias this settings class reads from the environment. pydantic-
# settings' env source reads real process environment variables regardless
# of `_env_file=None` (that only disables the .env FILE) -- if the ambient
# shell happens to export one of these (as this project's own .env does, and
# some shells source it directly), the "defaults" test would silently assert
# against whatever the shell happens to have rather than the class defaults.
_ALL_ALIASES = (
    "CHUNK_TOKEN_COUNTER_PROVIDER",
    "CHUNK_TOKENIZER_MODEL",
    "CHUNK_TOKENIZER_LOCAL_ONLY",
    "CHUNK_USE_LAYOUT_FRONT_MATTER_SIGNAL",
    "CHUNK_FRONT_MATTER_MAX_PAGE",
    "CHUNK_CONTENTS_RECOVERY_LATE_PAGE_THRESHOLD",
    "CHUNK_CROSS_REFERENCE_DETECTION_ENABLED",
    "CHUNK_CROSS_REFERENCE_PDF_LINKS_ENABLED",
)


def test_chunking_settings_defaults(monkeypatch) -> None:
    for alias in _ALL_ALIASES:
        monkeypatch.delenv(alias, raising=False)

    settings = ChunkingSettings(_env_file=None)

    assert settings.token_counter_provider == "transformer"
    assert settings.tokenizer_model is None
    assert settings.tokenizer_local_only is True
    assert settings.use_layout_front_matter_signal is False
    assert settings.front_matter_max_page == 2
    assert settings.contents_recovery_late_page_threshold == 3


def test_chunking_settings_use_layout_front_matter_signal_overridable_via_env(
    monkeypatch,
) -> None:
    monkeypatch.setenv("CHUNK_USE_LAYOUT_FRONT_MATTER_SIGNAL", "true")

    settings = ChunkingSettings()

    assert settings.use_layout_front_matter_signal is True


def test_chunking_settings_front_matter_page_thresholds_overridable_via_env(
    monkeypatch,
) -> None:
    monkeypatch.setenv("CHUNK_FRONT_MATTER_MAX_PAGE", "4")
    monkeypatch.setenv("CHUNK_CONTENTS_RECOVERY_LATE_PAGE_THRESHOLD", "6")

    settings = ChunkingSettings()

    assert settings.front_matter_max_page == 4
    assert settings.contents_recovery_late_page_threshold == 6
