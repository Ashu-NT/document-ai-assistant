from __future__ import annotations

from pathlib import Path

from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.config.paths import PROJECT_ROOT
from src.config.yaml_config_loader import load_yaml_config

_CONFIG_PATH = PROJECT_ROOT / "src" / "config" / "retrieval_intent" / "intent_top_k.yaml"

_cache: dict[RetrievalQueryIntent, int] | None = None


def _load(config_path: Path) -> dict[RetrievalQueryIntent, int]:
    data = load_yaml_config(
        config_path,
        description="Retrieval intent top-k overrides config",
    )
    overrides = data.get("overrides") or {}
    resolved: dict[RetrievalQueryIntent, int] = {}
    for key, value in overrides.items():
        try:
            intent = RetrievalQueryIntent(str(key))
        except ValueError:
            continue
        resolved[intent] = int(value)
    return resolved


def intent_top_k_overrides(
    *, config_path: Path | None = None
) -> dict[RetrievalQueryIntent, int]:
    if config_path is not None:
        return _load(config_path)

    global _cache
    if _cache is None:
        _cache = _load(_CONFIG_PATH)
    return _cache
