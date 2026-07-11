from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class PromptSectionTopologyView:
    section_key: str
    section_name: str
    section_path: str | None = None
    parent_section_path: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    source_numbers: list[int] = field(default_factory=list)
    direct_source_numbers: list[int] = field(default_factory=list)
    supporting_source_numbers: list[int] = field(default_factory=list)
    contextual_source_numbers: list[int] = field(default_factory=list)
    table_source_numbers: list[int] = field(default_factory=list)
