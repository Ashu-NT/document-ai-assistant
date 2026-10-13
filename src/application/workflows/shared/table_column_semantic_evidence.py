from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from src.application.workflows.shared.table_column_semantic_role import (
    TableColumnSemanticRole,
)


class EvidenceCategory(StrEnum):
    """Minimal evidence grouping for column semantic resolution. Each
    category has a distinct failure mode worth reasoning about separately:
    LEXICAL is fast but shallow (header text alone), STRUCTURAL inherits
    upstream shape-classification confidence (including its mistakes),
    CONTENT is robust but needs enough rows, CONTEXTUAL is reused from the
    existing whole-table classifier, RELATIONAL requires other columns to
    already be scored.
    """

    LEXICAL = "lexical"
    STRUCTURAL = "structural"
    CONTENT = "content"
    CONTEXTUAL = "contextual"
    RELATIONAL = "relational"


@dataclass(slots=True, frozen=True)
class ColumnSemanticEvidence:
    """One compact, non-redundant vote (or neutral observation) about a
    column's semantic role. Never duplicates raw table rows/cells -- only a
    short machine-readable description and reference. `role` is None for a
    neutral/bookkeeping observation (e.g. "header examined, no match")
    that did not cast a vote for or against any role.

    `deduplicated` is pure PROVENANCE, kept deliberately separate from
    `category` (which is the evidence TYPE, unchanged by this field):
    True means this specific item's contribution was zeroed because it
    reproduced another item derived from the identical, already-counted
    source text (see TableColumnSemanticClassifier's correlated-evidence
    deduplication). It is a structural fact about where the weight went,
    not a semantic judgment -- it does NOT mean "independent" when False,
    and a False item is not thereby "corroborating" anything; whether any
    given evidence category constitutes genuine independent semantic
    corroboration is a separate, unresolved question this field does not
    answer (see the evidence-weighting diagnostic report).
    """

    category: EvidenceCategory
    role: TableColumnSemanticRole | None
    description: str
    weight: float
    deduplicated: bool = False
