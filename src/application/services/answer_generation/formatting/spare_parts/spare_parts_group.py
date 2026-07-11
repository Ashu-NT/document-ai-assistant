from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SparePartsGroup:
    section_title: str
    section_path: str | None
    page_start: int | None
    page_end: int | None
    rows: list[dict[str, str]]
    raw_rows: list[str]
    partial: bool
    dropped_row_count: int = 0
