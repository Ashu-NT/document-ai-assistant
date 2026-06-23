from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class DocumentOverview:
    document_id: str
    title: str | None
    file_name: str
    document_type: str
    language: str | None
    page_count: int | None
    section_count: int
    chunk_count: int
    table_count: int
    picture_count: int
    identifier_count: int


@dataclass(slots=True, frozen=True)
class SectionEntry:
    section_id: str
    title: str
    level: int
    parent_section_id: str | None
    section_path: list[str]
    overview_text: str | None = None
    chunk_type_signals: list[str] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class IdentifierEntry:
    identifier_id: str
    raw_value: str
    identifier_type: str
    normalized_value: str | None


@dataclass(slots=True, frozen=True)
class TableEntry:
    table_id: str
    caption: str | None
    section_title: str | None
    page: int | None


@dataclass(slots=True, frozen=True)
class AssetEntry:
    picture_id: str
    caption: str | None
    section_title: str | None
    page: int | None
    has_ocr_text: bool


@dataclass(slots=True, frozen=True)
class DocumentCoverage:
    chunk_type_counts: dict[str, int]
    has_tables: bool
    has_pictures: bool
    has_identifiers: bool
    has_sections: bool


@dataclass(slots=True, frozen=True)
class DocumentExplorationResult:
    document_id: str
    overview: DocumentOverview
    sections: list[SectionEntry] = field(default_factory=list)
    identifiers: list[IdentifierEntry] = field(default_factory=list)
    tables: list[TableEntry] = field(default_factory=list)
    assets: list[AssetEntry] = field(default_factory=list)
    coverage: DocumentCoverage = field(
        default_factory=lambda: DocumentCoverage(
            chunk_type_counts={},
            has_tables=False,
            has_pictures=False,
            has_identifiers=False,
            has_sections=False,
        )
    )
