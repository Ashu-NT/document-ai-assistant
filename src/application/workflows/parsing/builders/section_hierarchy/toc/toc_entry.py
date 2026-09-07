import re
from dataclasses import dataclass, field


@dataclass(slots=True)
class TocEntry:
    title: str
    normalized_title: str
    start_page: int
    level_hint: int
    numbering: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "normalized_title": self.normalized_title,
            "start_page": self.start_page,
            "level_hint": self.level_hint,
            "numbering": self.numbering,
        }


@dataclass(slots=True)
class TocOutline:
    toc_header_id: str | None = None
    entries: list[TocEntry] = field(default_factory=list)
    matched_entries: dict[str, TocEntry] = field(default_factory=dict)
    header_numberings: dict[str, str] = field(default_factory=dict)
    unmatched_entries: list[TocEntry] = field(default_factory=list)
    # Headers with an exact TOC title match but conflicting explicit
    # numbering (e.g. TOC "1.9 Liability and Warranty" vs body heading "1.8
    # Liability and Warranty") - recorded for visibility only, since
    # TocHeaderMatcher still hard-rejects these as a match to avoid
    # false-positive TOC-to-heading links.
    numbering_drift_evidence: list[dict[str, object]] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "toc_header_id": self.toc_header_id,
            "entries": [entry.to_dict() for entry in self.entries],
            "matched_entries": {
                header_id: entry.to_dict()
                for header_id, entry in self.matched_entries.items()
            },
            "header_numberings": dict(self.header_numberings),
            "unmatched_entries": [
                entry.to_dict() for entry in self.unmatched_entries
            ],
            "numbering_drift_evidence": [
                dict(item) for item in self.numbering_drift_evidence
            ],
        }


def normalize_toc_title(value: str | None) -> str:
    if not value:
        return ""

    text = value.casefold()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
