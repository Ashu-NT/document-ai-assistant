from src.application.workflows.parsing.tables.semantics.table_body_text_extractor import (
    TableBodyTextExtractor,
)
from src.application.workflows.parsing.tables.semantics.table_category import (
    TableCategory,
)
from src.application.workflows.parsing.tables.semantics.table_matrix_detector import (
    TableMatrixDetector,
)
from src.application.workflows.parsing.tables.semantics.table_semantic_rule_evaluator import (
    TableSemanticRuleEvaluator,
)
from src.application.workflows.parsing.tables.semantics.table_specification_rule_evaluator import (
    TableSpecificationRuleEvaluator,
)
from src.application.workflows.parsing.tables.semantics.table_structured_list_classifier import (
    TableStructuredListClassifier,
)
from src.application.workflows.parsing.tables.semantics.table_text_signal_matcher import (
    TableTextSignalMatcher,
)
from src.domain.assets.table_rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)
from src.domain.assets import TableAsset


class TableSemanticClassifier:
    def __init__(
        self,
        *,
        matrix_detector: TableMatrixDetector | None = None,
        row_canonicalizer: TableRowCanonicalizer | None = None,
        signal_matcher: TableTextSignalMatcher | None = None,
        structured_list_classifier: TableStructuredListClassifier | None = None,
        rule_evaluator: TableSemanticRuleEvaluator | None = None,
        specification_rule_evaluator: TableSpecificationRuleEvaluator | None = None,
        body_text_extractor: TableBodyTextExtractor | None = None,
    ) -> None:
        self.matrix_detector = matrix_detector or TableMatrixDetector()
        self.row_canonicalizer = row_canonicalizer or TableRowCanonicalizer()
        self.signal_matcher = signal_matcher or TableTextSignalMatcher()
        self.structured_list_classifier = (
            structured_list_classifier
            or TableStructuredListClassifier(signal_matcher=self.signal_matcher)
        )
        self.rule_evaluator = rule_evaluator or TableSemanticRuleEvaluator(
            signal_matcher=self.signal_matcher
        )
        self.specification_rule_evaluator = (
            specification_rule_evaluator
            or TableSpecificationRuleEvaluator(signal_matcher=self.signal_matcher)
        )
        self.body_text_extractor = body_text_extractor or TableBodyTextExtractor(
            signal_matcher=self.signal_matcher
        )

    def classify(
        self,
        *,
        table: TableAsset,
        caption: str | None = None,
        nearby_text: str | None = None,
        section_path: list[str] | None = None,
        item_label: str | None = None,
    ) -> tuple[TableCategory, float]:
        rows = self.row_canonicalizer.canonicalize(table.rows)
        has_header_row = self.row_canonicalizer.has_explicit_header_row(rows)
        headers = [
            str(cell or "").strip().casefold()
            for cell in (rows[0] if has_header_row and rows else [])
        ]
        body_rows = rows[1:] if has_header_row else rows
        label_cells = self.body_text_extractor.body_label_cells(
            body_rows,
            has_header_row=has_header_row,
        )
        body_text = self.body_text_extractor.body_text(body_rows)
        header_text = self.signal_matcher.normalized_text(*headers)
        direct_text = self.signal_matcher.normalized_text(
            header_text,
            *label_cells,
            body_text,
            caption,
            nearby_text,
            table.markdown,
        )
        section_text = self.signal_matcher.normalized_text(" > ".join(section_path or []))
        fallback_text = " ".join(part for part in [direct_text, section_text] if part)

        if (
            item_label == "document_index"
            or self.signal_matcher.contains(fallback_text, "table of contents")
            or self.signal_matcher.contains(fallback_text, "contents")
        ):
            return TableCategory.TOC_TABLE, 0.99
        if self.matrix_detector.is_maintenance_interval_matrix(table.rows):
            return TableCategory.MAINTENANCE_INTERVAL_TABLE, 0.92
        if self.rule_evaluator.looks_like_maintenance_interval_table(
            headers,
            label_cells,
            direct_text,
        ):
            return TableCategory.MAINTENANCE_INTERVAL_TABLE, 0.89
        if self.rule_evaluator.looks_like_lubrication_schedule_table(
            headers,
            label_cells,
            direct_text,
            section_text,
        ):
            return TableCategory.MAINTENANCE_INTERVAL_TABLE, 0.87
        if self.rule_evaluator.looks_like_troubleshooting_table(
            headers,
            direct_text,
            section_text,
        ):
            return TableCategory.TROUBLESHOOTING_TABLE, 0.9
        if self.structured_list_classifier.looks_like_spare_parts_table(
            headers=headers,
            labels=label_cells,
            body_rows=body_rows,
            direct_text=direct_text,
            section_text=section_text,
        ):
            return TableCategory.SPARE_PARTS_TABLE, 0.9
        if self.specification_rule_evaluator.looks_like_operation_reference_table(
            headers,
            label_cells,
            direct_text,
            section_text,
        ):
            return TableCategory.OPERATION_REFERENCE_TABLE, 0.84
        if self.specification_rule_evaluator.looks_like_operating_limits_table(
            headers,
            label_cells,
            direct_text,
        ):
            return TableCategory.OPERATING_LIMITS_TABLE, 0.86
        if self.specification_rule_evaluator.looks_like_technical_data_table(
            headers,
            label_cells,
            direct_text,
            section_text,
        ):
            return TableCategory.TECHNICAL_DATA_TABLE, 0.88
        if self.specification_rule_evaluator.looks_like_certification_table(
            direct_text,
            section_text,
        ):
            return TableCategory.CERTIFICATION_TABLE, 0.82
        if self.structured_list_classifier.looks_like_connection_table(
            headers=headers,
            direct_text=direct_text,
        ):
            return TableCategory.CONNECTION_TABLE, 0.8
        if self.structured_list_classifier.looks_like_sensor_instrument_table(
            headers=headers,
            direct_text=direct_text,
        ):
            return TableCategory.SENSOR_INSTRUMENT_TABLE, 0.78
        if self.structured_list_classifier.looks_like_identifier_table(
            headers=headers,
            labels=label_cells,
            body_rows=body_rows,
            direct_text=direct_text,
            section_text=section_text,
        ):
            return TableCategory.IDENTIFIER_TABLE, 0.76
        return TableCategory.GENERAL_TABLE, 0.4
