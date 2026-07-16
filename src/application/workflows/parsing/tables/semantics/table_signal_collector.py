from __future__ import annotations

from src.application.workflows.parsing.tables.semantics.table_semantic_rule_evaluator import (
    TableSemanticRuleEvaluator,
)
from src.application.workflows.parsing.tables.semantics.table_specification_rule_evaluator import (
    TableSpecificationRuleEvaluator,
)
from src.application.workflows.parsing.tables.semantics.table_structured_list_classifier import (
    TableStructuredListClassifier,
)
from src.application.workflows.parsing.tables.semantics.table_matrix_detector import (
    TableMatrixDetector,
)
from src.application.workflows.shared.table_signal import TableSignal


class TableSignalCollector:
    def __init__(
        self,
        *,
        matrix_detector: TableMatrixDetector,
        rule_evaluator: TableSemanticRuleEvaluator,
        specification_rule_evaluator: TableSpecificationRuleEvaluator,
        structured_list_classifier: TableStructuredListClassifier,
    ) -> None:
        self.matrix_detector = matrix_detector
        self.rule_evaluator = rule_evaluator
        self.specification_rule_evaluator = specification_rule_evaluator
        self.structured_list_classifier = structured_list_classifier

    def collect(
        self,
        *,
        rows: list[list[str]],
        headers: list[str],
        label_cells: list[str],
        body_rows: list[list[str]],
        direct_text: str,
        section_text: str,
    ) -> frozenset[TableSignal]:
        signals: set[TableSignal] = set()
        if (
            self.matrix_detector.is_maintenance_interval_matrix(rows)
            or self.rule_evaluator.looks_like_maintenance_interval_table(
                headers, label_cells, direct_text
            )
            or self.rule_evaluator.looks_like_lubrication_schedule_table(
                headers, label_cells, direct_text, section_text
            )
        ):
            signals.update(
                {TableSignal.MAINTENANCE_INTERVALS, TableSignal.SCHEDULES}
            )
        if self.rule_evaluator.looks_like_troubleshooting_table(
            headers, direct_text, section_text
        ):
            signals.add(TableSignal.TROUBLESHOOTING)
        if self.structured_list_classifier.looks_like_spare_parts_table(
            headers=headers,
            labels=label_cells,
            body_rows=body_rows,
            direct_text=direct_text,
            section_text=section_text,
        ):
            signals.add(TableSignal.SPARE_PARTS)
        if self.specification_rule_evaluator.looks_like_operating_limits_table(
            headers, label_cells, direct_text
        ):
            signals.add(TableSignal.OPERATING_LIMITS)
        if self.specification_rule_evaluator.looks_like_technical_data_table(
            headers, label_cells, direct_text, section_text
        ):
            signals.add(TableSignal.SPECIFICATIONS)
        if self.specification_rule_evaluator.looks_like_certification_table(
            direct_text, section_text
        ):
            signals.add(TableSignal.CERTIFICATION)
        if self.structured_list_classifier.looks_like_connection_table(
            headers=headers,
            direct_text=direct_text,
        ):
            signals.add(TableSignal.CONNECTIONS)
        if self.structured_list_classifier.looks_like_sensor_instrument_table(
            headers=headers,
            direct_text=direct_text,
        ):
            signals.add(TableSignal.SENSOR_DATA)
        if self.structured_list_classifier.looks_like_identifier_table(
            headers=headers,
            labels=label_cells,
            body_rows=body_rows,
            direct_text=direct_text,
            section_text=section_text,
        ):
            signals.add(TableSignal.IDENTIFIERS)
        return frozenset(signals)
