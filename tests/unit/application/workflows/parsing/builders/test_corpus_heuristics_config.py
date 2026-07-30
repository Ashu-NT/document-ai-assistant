from src.application.workflows.parsing.builders.section_hierarchy.corpus_heuristics_config import (
    branding_headers,
    umbrella_words,
)


def test_branding_headers_loads_shipped_config() -> None:
    result = branding_headers()

    assert "environmentally responsible solutions engineered" in result


def test_umbrella_words_loads_shipped_config() -> None:
    result = umbrella_words()

    assert "controls" in result
    assert "waveforms" in result


def test_branding_headers_config_path_override(tmp_path) -> None:
    config_path = tmp_path / "corpus_heuristics.yaml"
    config_path.write_text(
        "branding_headers:\n  - \"Custom Boilerplate\"\numbrella_words:\n  - \"widgets\"\n",
        encoding="utf-8",
    )

    assert branding_headers(config_path=config_path) == {"custom boilerplate"}
    assert umbrella_words(config_path=config_path) == {"widgets"}
