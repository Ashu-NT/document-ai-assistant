from __future__ import annotations

from dataclasses import dataclass, field

from src.application.workflows.shared.table_column_resolution_state import (
    ColumnResolutionState,
)
from src.application.workflows.shared.table_column_semantic_evidence import (
    ColumnSemanticEvidence,
)
from src.application.workflows.shared.table_column_semantic_role import (
    TableColumnSemanticRole,
)


@dataclass(slots=True, frozen=True)
class ColumnSemanticResolution:
    """Result of resolving ONE column's semantic role. `source_header` and
    `structural_header` are kept permanently separate -- the former is the
    literal text from the table's own header row, the latter is whatever
    label an upstream structural interpretation (header_paths/axis
    reasoning) assigned to this position. They are allowed to diverge (and
    sometimes do, e.g. a table whose real header says "Task" while its
    structural interpretation displays "Parameter"); neither may silently
    stand in for the other anywhere in this contract.
    """

    column_index: int
    source_header: str | None
    structural_header: str | None
    resolution_state: ColumnResolutionState
    semantic_role: TableColumnSemanticRole | None
    confidence: float | None
    candidate_roles: tuple[tuple[TableColumnSemanticRole, float], ...] = field(
        default_factory=tuple
    )
    evidence: tuple[ColumnSemanticEvidence, ...] = field(default_factory=tuple)


@dataclass(slots=True, frozen=True)
class TableColumnSemantics:
    """All column resolutions for one table, computed deterministically and
    on demand from already-persisted TableAsset fields -- never itself
    persisted (see PHASE 2B SHARED TABLE COLUMN SEMANTIC RESOLUTION DESIGN,
    Strategy 2)."""

    table_id: str
    columns: tuple[ColumnSemanticResolution, ...]
    classifier_version: str
