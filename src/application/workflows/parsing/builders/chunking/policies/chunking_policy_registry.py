from __future__ import annotations

from pathlib import Path

from src.application.workflows.parsing.builders.chunking.policies.chunking_policy_loader import (
    load_policy_from_yaml,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.document_chunking_policy import (
    DocumentChunkingPolicy,
)


class ChunkingPolicyRegistry:
    """Cached, YAML-backed registry of chunking policies.

    Falls back to None when a YAML file is absent or unparseable — callers
    should then use their hardcoded Python defaults.
    """

    def __init__(self, config_dir: Path | None = None) -> None:
        self._config_dir = config_dir
        self._cache: dict[ChunkingProfile, DocumentChunkingPolicy | None] = {}

    def get(self, profile: ChunkingProfile) -> DocumentChunkingPolicy | None:
        if profile not in self._cache:
            self._cache[profile] = load_policy_from_yaml(
                profile, config_dir=self._config_dir
            )
        return self._cache[profile]

    def clear(self) -> None:
        self._cache.clear()


_default_registry: ChunkingPolicyRegistry | None = None


def default_registry() -> ChunkingPolicyRegistry:
    global _default_registry
    if _default_registry is None:
        _default_registry = ChunkingPolicyRegistry()
    return _default_registry
