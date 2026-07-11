from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class PromptSourceGroupView:
    group_name: str
    chunk_type: str | None = None
    source_numbers: list[int] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class PromptSectionGroupView:
    group_name: str
    section_path: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    source_numbers: list[int] = field(default_factory=list)
