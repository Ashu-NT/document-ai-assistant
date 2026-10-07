from __future__ import annotations

from dataclasses import dataclass, field

from src.application.evaluation.table_semantics.human_semantic_status import (
    HumanSemanticStatus,
)
from src.application.evaluation.table_semantics.table_semantic_evaluation_outcome import (
    TableSemanticEvaluationOutcome,
)
from src.application.evaluation.table_semantics.table_semantic_golden_case import (
    ColumnSemanticGoldenCase,
)
from src.application.evaluation.table_semantics.table_semantic_locator import (
    load_cached_document_graph,
    locate_real_table,
)
from src.application.workflows.shared.table_column_resolution_state import (
    ColumnResolutionState,
)
from src.application.workflows.shared.table_column_semantic_classifier import (
    TableColumnSemanticClassifier,
)
from src.application.workflows.shared.table_column_semantic_resolution import (
    ColumnSemanticResolution,
)
from src.shared.ids import IdGenerator

# Isolated evaluator: loads reviewed golden cases, re-locates each real
# table, runs the UNMODIFIED TableColumnSemanticClassifier against it, and
# compares classifier output to human-reviewed source truth. Never modifies
# classifier behavior/thresholds/aliases/roles/parsing, never calls an LLM.


@dataclass(slots=True, frozen=True)
class TableSemanticEvaluationRow:
    golden: ColumnSemanticGoldenCase
    classifier_resolution: ColumnSemanticResolution | None
    outcome: TableSemanticEvaluationOutcome


@dataclass(slots=True, frozen=True)
class TableSemanticEvaluationResult:
    rows: tuple[TableSemanticEvaluationRow, ...] = field(default_factory=tuple)

    def reviewed_rows(self) -> tuple[TableSemanticEvaluationRow, ...]:
        return tuple(
            row for row in self.rows
            if row.outcome != TableSemanticEvaluationOutcome.UNREVIEWED_OR_UNLOCATABLE
        )

    def count(self, outcome: TableSemanticEvaluationOutcome) -> int:
        return sum(1 for row in self.reviewed_rows() if row.outcome == outcome)

    @property
    def resolved_total(self) -> int:
        return self.count(TableSemanticEvaluationOutcome.CORRECT_RESOLUTION) + self.count(
            TableSemanticEvaluationOutcome.FALSE_RESOLUTION
        )

    @property
    def resolved_precision(self) -> float | None:
        total = self.resolved_total
        if total == 0:
            return None
        return self.count(TableSemanticEvaluationOutcome.CORRECT_RESOLUTION) / total

    @property
    def knowable_total(self) -> int:
        """Columns where human truth is KNOWN_MAPPED -- the denominator for
        resolution coverage (how much of what COULD be resolved, was)."""
        return sum(
            1
            for row in self.reviewed_rows()
            if row.golden.human_status == HumanSemanticStatus.KNOWN_MAPPED
        )

    @property
    def resolution_coverage(self) -> float | None:
        total = self.knowable_total
        if total == 0:
            return None
        return self.count(TableSemanticEvaluationOutcome.CORRECT_RESOLUTION) / total


class TableSemanticEvaluator:
    def __init__(self, *, classifier: TableColumnSemanticClassifier | None = None) -> None:
        self.classifier = classifier or TableColumnSemanticClassifier()

    def evaluate(self, golden_cases: list[ColumnSemanticGoldenCase]) -> TableSemanticEvaluationResult:
        id_generator = IdGenerator()
        rows: list[TableSemanticEvaluationRow] = []

        # Group by table locator so each table is parsed/located once.
        resolutions_by_table: dict[tuple, dict[int, ColumnSemanticResolution] | None] = {}

        for case in golden_cases:
            if not case.is_reviewed:
                rows.append(
                    TableSemanticEvaluationRow(
                        golden=case,
                        classifier_resolution=None,
                        outcome=TableSemanticEvaluationOutcome.UNREVIEWED_OR_UNLOCATABLE,
                    )
                )
                continue

            key = case.table_locator_key
            if key not in resolutions_by_table:
                resolutions_by_table[key] = self._classify_table(case, id_generator=id_generator)
            column_resolutions = resolutions_by_table[key]

            if column_resolutions is None or case.column_index not in column_resolutions:
                rows.append(
                    TableSemanticEvaluationRow(
                        golden=case,
                        classifier_resolution=None,
                        outcome=TableSemanticEvaluationOutcome.UNREVIEWED_OR_UNLOCATABLE,
                    )
                )
                continue

            resolution = column_resolutions[case.column_index]
            outcome = self._compare(case, resolution)
            rows.append(
                TableSemanticEvaluationRow(
                    golden=case, classifier_resolution=resolution, outcome=outcome
                )
            )

        return TableSemanticEvaluationResult(rows=tuple(rows))

    def _classify_table(
        self, case: ColumnSemanticGoldenCase, *, id_generator: IdGenerator
    ) -> dict[int, ColumnSemanticResolution] | None:
        try:
            graph = load_cached_document_graph(case.document_title, id_generator=id_generator)
        except FileNotFoundError:
            return None

        table = locate_real_table(
            graph,
            table_category=case.table_category,
            header_substring=case.header_substring,
            occurrence_index=case.occurrence_index,
        )
        if table is None:
            return None

        semantics = self.classifier.classify(table)
        return {col.column_index: col for col in semantics.columns}

    @staticmethod
    def _compare(
        case: ColumnSemanticGoldenCase, resolution: ColumnSemanticResolution
    ) -> TableSemanticEvaluationOutcome:
        state = resolution.resolution_state
        human = case.human_status

        if human == HumanSemanticStatus.KNOWN_UNMAPPED:
            return TableSemanticEvaluationOutcome.KNOWN_UNMAPPED_HANDLING

        if state == ColumnResolutionState.RESOLVED:
            if human == HumanSemanticStatus.KNOWN_MAPPED and resolution.semantic_role == case.human_role:
                return TableSemanticEvaluationOutcome.CORRECT_RESOLUTION
            return TableSemanticEvaluationOutcome.FALSE_RESOLUTION

        if state == ColumnResolutionState.AMBIGUOUS:
            if human == HumanSemanticStatus.KNOWN_MAPPED:
                return TableSemanticEvaluationOutcome.SAFE_ABSTENTION_AMBIGUOUS
            if human == HumanSemanticStatus.GENUINELY_AMBIGUOUS:
                return TableSemanticEvaluationOutcome.CORRECT_AMBIGUITY
            # human == UNKNOWN: an honest abstention either way, closest to
            # correct_unknown in spirit but the state differs -- report as
            # safe_abstention_unknown-adjacent via correct_unknown only when
            # the states literally match; otherwise treat conservatively.
            return TableSemanticEvaluationOutcome.CORRECT_AMBIGUITY

        # state in {UNKNOWN, UNMAPPED}
        if human == HumanSemanticStatus.KNOWN_MAPPED:
            return TableSemanticEvaluationOutcome.SAFE_ABSTENTION_UNKNOWN
        if human == HumanSemanticStatus.UNKNOWN:
            return TableSemanticEvaluationOutcome.CORRECT_UNKNOWN
        # human == GENUINELY_AMBIGUOUS but classifier abstained as
        # UNKNOWN/UNMAPPED rather than AMBIGUOUS -- still a safe, honest
        # abstention, closest to correct_unknown (no false confidence).
        return TableSemanticEvaluationOutcome.CORRECT_UNKNOWN
