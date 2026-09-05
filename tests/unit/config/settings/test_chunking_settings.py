from src.config.settings.chunking_settings import ChunkingSettings


def test_chunking_settings_defaults() -> None:
    settings = ChunkingSettings(_env_file=None)

    assert settings.token_counter_provider == "transformer"
    assert settings.tokenizer_model is None
    assert settings.tokenizer_local_only is True
    assert settings.use_layout_front_matter_signal is False


def test_chunking_settings_use_layout_front_matter_signal_overridable_via_env(
    monkeypatch,
) -> None:
    monkeypatch.setenv("CHUNK_USE_LAYOUT_FRONT_MATTER_SIGNAL", "true")

    settings = ChunkingSettings()

    assert settings.use_layout_front_matter_signal is True
