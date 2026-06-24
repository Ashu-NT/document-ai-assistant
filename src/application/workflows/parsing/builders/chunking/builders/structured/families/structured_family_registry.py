from __future__ import annotations

from pathlib import Path

from src.application.workflows.parsing.builders.chunking.builders.structured.families.structured_family_config_loader import (
    FamilyConfig,
    load_family_configs,
)


class StructuredFamilyRegistry:
    """Registry that maps family names to their configuration.

    Used by StructuredFamilySpecFactory to determine the ordered list of
    enabled families without hardcoding it in Python source.  Falls back
    gracefully when YAML files are missing.
    """

    def __init__(self, config_dir: Path | None = None) -> None:
        self._config_dir = config_dir
        self._configs: list[FamilyConfig] | None = None

    def _ensure_loaded(self) -> None:
        if self._configs is None:
            self._configs = load_family_configs(self._config_dir)

    def all_configs(self) -> list[FamilyConfig]:
        self._ensure_loaded()
        return list(self._configs or [])

    def enabled_builder_class_names(self) -> list[str]:
        return [c.builder_class for c in self.all_configs() if c.enabled]

    def is_family_enabled(self, family: str) -> bool:
        return any(c.family == family and c.enabled for c in self.all_configs())

    def clear(self) -> None:
        self._configs = None


_default_registry: StructuredFamilyRegistry | None = None


def default_family_registry() -> StructuredFamilyRegistry:
    global _default_registry
    if _default_registry is None:
        _default_registry = StructuredFamilyRegistry()
    return _default_registry
