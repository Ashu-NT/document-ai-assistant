from __future__ import annotations

from dataclasses import dataclass, field

from src.application.evaluation.table_semantics.human_semantic_status import (
    HumanSemanticStatus,
)
from src.application.evaluation.table_semantics.table_semantic_review_status import (
    TableSemanticReviewStatus,
)
from src.application.workflows.shared.table_column_semantic_role import (
    TableColumnSemanticRole,
)


@dataclass(slots=True, frozen=True)
class ColumnSemanticGoldenCase:
    """One human-reviewed golden judgment about ONE column's SOURCE
    semantic truth in ONE real table. Deliberately does not reference
    table_id -- table_id is generated fresh by IdGenerator on every parse
    call and is NOT stable across separate parse invocations of the same
    cached document (even though the table's content/order is
    deterministic). A table is instead re-located deterministically, on
    demand, by (document_title, table_category, header_substring,
    occurrence_index) -- see `table_semantic_locator.locate_real_table`.
    """

    # --- table locator (stable across re-parses of the same cached doc) ---
    document_title: str
    table_category: str
    header_substring: str | None
    occurrence_index: int

    # --- informational context, not used for matching ---
    section_path: tuple[str, ...] = field(default_factory=tuple)

    # --- the reviewed column itself ---
    column_index: int = 0
    source_header: str | None = None

    # --- human-reviewed SOURCE TRUTH (never a classifier prediction) ---
    human_status: HumanSemanticStatus = HumanSemanticStatus.UNKNOWN
    human_role: TableColumnSemanticRole | None = None
    human_concept: str | None = None
    review_status: TableSemanticReviewStatus = TableSemanticReviewStatus.CANDIDATE
    notes: str = ""

    @property
    def is_reviewed(self) -> bool:
        return self.review_status == TableSemanticReviewStatus.REVIEWED

    @property
    def table_locator_key(self) -> tuple[str, str, str | None, int]:
        return (
            self.document_title,
            self.table_category,
            self.header_substring,
            self.occurrence_index,
        )
