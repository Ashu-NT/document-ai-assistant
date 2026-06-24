from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MarkerSet:
    """Named collection of string marker tuples loaded from YAML or Python constants."""

    name: str
    markers: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def get(self, key: str) -> tuple[str, ...]:
        return self.markers.get(key, ())

    def get_or_default(self, key: str, default: tuple[str, ...]) -> tuple[str, ...]:
        value = self.markers.get(key)
        if value is None:
            return default
        return value
