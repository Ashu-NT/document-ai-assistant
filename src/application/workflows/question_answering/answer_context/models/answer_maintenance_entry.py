from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AnswerMaintenanceReference:
    source_number: int
    page_start: int | None = None
    page_end: int | None = None
    section_path: str | None = None


@dataclass(slots=True)
class AnswerMaintenanceEntry:
    """`references` is the single source of truth for per-source page/section
    provenance. Previously `source_numbers`, `section_paths`, `page_start`,
    and `section_path` were also stored as separate fields covering the
    exact same facts as `references[*]`, kept in sync by hand on every
    construction/merge with nothing enforcing that they actually agreed
    (plan section 4.13). Only `source_number` remains a real field --
    matching `AnswerKeyValue.source_number`'s own convention for "the
    primary source this fact came from" -- everything else below is
    derived from `references`."""

    task: str
    interval: str
    component: str | None
    notes: str | None
    source_number: int
    description: str | None = None
    references: list[AnswerMaintenanceReference] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.references:
            self.references = [
                AnswerMaintenanceReference(source_number=self.source_number)
            ]
            return
        # `references` owns provenance. If a caller passes explicit
        # references, keep the scalar "primary source" field aligned to the
        # first reference instead of letting two parallel representations
        # drift out of sync again.
        self.source_number = self.references[0].source_number

    @property
    def source_numbers(self) -> list[int]:
        return [reference.source_number for reference in self.references]

    @property
    def section_paths(self) -> list[str]:
        return [
            reference.section_path
            for reference in self.references
            if reference.section_path
        ]

    @property
    def page_start(self) -> int | None:
        return self.references[0].page_start if self.references else None

    @property
    def page_end(self) -> int | None:
        return self.references[0].page_end if self.references else None

    @property
    def section_path(self) -> str | None:
        return self.references[0].section_path if self.references else None
