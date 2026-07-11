from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RawSourceBudget:
    max_sources: int
    max_chars_per_source: int
