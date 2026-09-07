from __future__ import annotations

from pathlib import Path

from src.config.paths import PROJECT_ROOT
from src.config.yaml_config_loader import load_yaml_config

_CONFIG_PATH = (
    PROJECT_ROOT / "src" / "config" / "section_hierarchy" / "corpus_heuristics.yaml"
)

_cache: dict[str, frozenset[str]] | None = None


def _load(config_path: Path) -> dict[str, frozenset[str]]:
    data = load_yaml_config(
        config_path,
        description="Section-hierarchy corpus heuristics config",
    )
    return {
        "branding_headers": frozenset(
            str(item).strip().lower() for item in data.get("branding_headers") or []
        ),
        "umbrella_words": frozenset(
            str(item).strip().lower() for item in data.get("umbrella_words") or []
        ),
    }


def branding_headers(*, config_path: Path | None = None) -> frozenset[str]:
    if config_path is not None:
        return _load(config_path)["branding_headers"]

    global _cache
    if _cache is None:
        _cache = _load(_CONFIG_PATH)
    return _cache["branding_headers"]


def umbrella_words(*, config_path: Path | None = None) -> frozenset[str]:
    if config_path is not None:
        return _load(config_path)["umbrella_words"]

    global _cache
    if _cache is None:
        _cache = _load(_CONFIG_PATH)
    return _cache["umbrella_words"]
