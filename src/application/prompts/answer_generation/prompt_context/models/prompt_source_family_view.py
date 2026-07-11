from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class PromptSourceFamilyView:
    family_id: str
    family_label: str
    anchor_source_number: int
    anchor_chunk_type: str | None = None
    section_path: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    direct_source_numbers: list[int] = field(default_factory=list)
    supporting_source_numbers: list[int] = field(default_factory=list)
    contextual_source_numbers: list[int] = field(default_factory=list)
    table_source_numbers: list[int] = field(default_factory=list)
