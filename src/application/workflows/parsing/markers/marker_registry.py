from __future__ import annotations

from pathlib import Path

from src.application.workflows.parsing.markers.marker_config_loader import (
    load_marker_set,
)
from src.application.workflows.parsing.markers.marker_set import MarkerSet


class MarkerRegistry:
    """Cached, YAML-backed registry of marker sets per document family.

    Falls back gracefully when YAML files are absent or pyyaml is not
    installed — callers should then use their Python constant defaults.
    """

    def __init__(self, config_dir: Path | None = None) -> None:
        self._config_dir = config_dir
        self._cache: dict[str, MarkerSet | None] = {}

    def get(self, family: str) -> MarkerSet | None:
        if family not in self._cache:
            self._cache[family] = load_marker_set(
                family, config_dir=self._config_dir
            )
        return self._cache[family]

    def get_markers(self, family: str, key: str) -> tuple[str, ...] | None:
        marker_set = self.get(family)
        if marker_set is None:
            return None
        value = marker_set.markers.get(key)
        return value

    def clear(self) -> None:
        self._cache.clear()


_default_registry: MarkerRegistry | None = None


def default_marker_registry() -> MarkerRegistry:
    global _default_registry
    if _default_registry is None:
        _default_registry = MarkerRegistry()
    return _default_registry
