from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NormalizedTableRows:
    headers: list[str]
    rows: list[list[str]]
