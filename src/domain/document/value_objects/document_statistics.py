from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class DocumentStatistics:
    page_count: int | None = None
    element_count: int = 0
    section_count: int = 0
    chunk_count: int = 0
    table_count: int = 0
    picture_count: int = 0
    identifier_count: int = 0
    chunk_type_counts: dict[str, int] = field(default_factory=dict)

    def has_pages(self) -> bool:
        return self.page_count is not None and self.page_count > 0