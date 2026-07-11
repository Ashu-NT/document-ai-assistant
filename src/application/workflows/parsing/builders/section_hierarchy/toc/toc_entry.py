import re
from dataclasses import dataclass, field


@dataclass(slots=True)
class TocEntry:
    title: str
    normalized_title: str
    start_page: int
    level_hint: int
    numbering: str | None = None


@dataclass(slots=True)
class TocOutline:
    toc_header_id: str | None = None
    entries: list[TocEntry] = field(default_factory=list)
    matched_entries: dict[str, TocEntry] = field(default_factory=dict)
    header_numberings: dict[str, str] = field(default_factory=dict)


def normalize_toc_title(value: str | None) -> str:
    if not value:
        return ""

    text = value.casefold()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
