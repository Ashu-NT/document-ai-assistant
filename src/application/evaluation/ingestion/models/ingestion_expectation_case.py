from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True, frozen=True)
class ExpectedCrossReference:
    # A distinguishing substring of the real cross-reference's matched_text
    # -- not an exact-match requirement, since minor whitespace/casing
    # differences in extraction shouldn't fail an otherwise-correct case.
    clue: str
    # None means "this clue must NOT resolve to an internal cross-reference"
    # (e.g. a citation of an external standard/directive).
    expected_reference_type: str | None = None
    expected_target_section: str | None = None
    expected_target_annex: str | None = None


@dataclass(slots=True, frozen=True)
class IngestionExpectationCase:
    case_id: str
    document_path: Path
    expected_document_type: str | None = None
    expected_section_count: int | None = None
    expected_top_level_section_titles: tuple[str, ...] = ()
    expected_chunk_count: int | None = None
    expected_chunk_type_counts: dict[str, int] = field(default_factory=dict)
    expected_cross_references: tuple[ExpectedCrossReference, ...] = ()
    expected_table_count: int | None = None
    expected_picture_count: int | None = None
    notes: str | None = None


__all__ = ["ExpectedCrossReference", "IngestionExpectationCase"]
