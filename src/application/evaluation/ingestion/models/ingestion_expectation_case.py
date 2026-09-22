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
    # Stable corpus alias this case's document_path was resolved from (see
    # GoldenCorpusManifest), when the case was authored with `document_alias`
    # instead of a literal path. None for cases that supplied a literal
    # `document_path` directly (e.g. ad hoc/test fixtures). Kept only for
    # traceability/reporting - document_path remains the one field every
    # other consumer (the evaluator, the runner script) actually uses.
    document_alias: str | None = None
    expected_document_type: str | None = None
    expected_section_count: int | None = None
    expected_top_level_section_titles: tuple[str, ...] = ()
    expected_chunk_count: int | None = None
    expected_chunk_type_counts: dict[str, int] = field(default_factory=dict)
    expected_cross_references: tuple[ExpectedCrossReference, ...] = ()
    expected_table_count: int | None = None
    expected_picture_count: int | None = None
    # Tolerant (min/max) counterparts to the exact fields above - use these
    # when a curated exact count would freeze today's Docling segmentation
    # as golden truth rather than genuinely reviewed behavior (see approved
    # decision "do not blindly freeze today's Docling segmentation counts").
    expected_element_count_min: int | None = None
    expected_element_count_max: int | None = None
    expected_chunk_count_min: int | None = None
    expected_chunk_count_max: int | None = None
    expected_table_count_min: int | None = None
    expected_table_count_max: int | None = None
    expected_picture_count_min: int | None = None
    expected_picture_count_max: int | None = None
    # Substrings that must appear somewhere in the parsed document's own
    # text, independent of cross-reference resolution - a cheap catastrophic
    # -truncation/regression detector ("critical text survives parsing").
    required_text_clues: tuple[str, ...] = ()
    # ChunkCrossReferenceType values (e.g. "section_reference") for which
    # `expected_cross_references` above is a COMPLETE, exhaustively reviewed
    # list of every reference of that type in this document - positive and
    # negative. Only for types listed here can false positives/precision be
    # computed (an actual reference of an unlisted type may simply be one
    # nobody has reviewed yet, not a wrong one). Leave empty until someone
    # has actually done that review; recall/true-positive/false-negative
    # metrics are always computable from the curated list regardless.
    exhaustive_cross_reference_types: tuple[str, ...] = ()
    notes: str | None = None


__all__ = ["ExpectedCrossReference", "IngestionExpectationCase"]
