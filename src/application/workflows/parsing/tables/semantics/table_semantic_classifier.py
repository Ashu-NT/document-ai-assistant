from dataclasses import dataclass

from src.application.workflows.parsing.tables.semantics.table_body_text_extractor import (
    TableBodyTextExtractor,
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
from src.application.workflows.shared.table_category import TableCategory
from src.application.workflows.shared.table_signal import TableSignal


@dataclass(slots=True, frozen=True)
class _ClassificationContext:
    headers: list[str]
    body_rows: list[list[str]]
    label_cells: list[str]
    direct_text: str
    section_text: str
    fallback_text: str


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

    def _build_context(
        self,
        *,
        table: TableAsset,
        caption: str | None,
        nearby_text: str | None,
        section_path: list[str] | None,
    ) -> _ClassificationContext:
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
        return _ClassificationContext(
            headers=headers,
            body_rows=body_rows,
            label_cells=label_cells,
            direct_text=direct_text,
            section_text=section_text,
            fallback_text=fallback_text,
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
        context = self._build_context(
            table=table,
            caption=caption,
            nearby_text=nearby_text,
            section_path=section_path,
        )
        headers = context.headers
        body_rows = context.body_rows
        label_cells = context.label_cells
        direct_text = context.direct_text
        section_text = context.section_text
        fallback_text = context.fallback_text

        if (
            item_label == "document_index"
            or self.signal_matcher.contains(fallback_text, "table of contents")
            # Bare "contents" is scoped to the section heading path only, not
            # the table's own body/caption text -- a real TOC lives under a
            # heading literally titled "Contents"/"Index", whereas the word
            # shows up incidentally in plenty of real spec/datasheet tables
            # ("oil contents", "tank contents", "package contents").
            or self.signal_matcher.contains(section_text, "contents")
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

    def detect_signals(
        self,
        *,
        table: TableAsset,
        caption: str | None = None,
        nearby_text: str | None = None,
        section_path: list[str] | None = None,
    ) -> frozenset[TableSignal]:
        """Multi-valued content signals, additive to `classify()`'s single
        category decision. Evaluates every rule (rather than stopping at
        the first match) so a table that e.g. matches spare-parts AND
        contains identifier-like columns keeps both facts instead of
        losing one to `classify()`'s first-match precedence.
        """
        context = self._build_context(
            table=table,
            caption=caption,
            nearby_text=nearby_text,
            section_path=section_path,
        )
        headers = context.headers
        body_rows = context.body_rows
        label_cells = context.label_cells
        direct_text = context.direct_text
        section_text = context.section_text

        signals: set[TableSignal] = set()

        if (
            self.matrix_detector.is_maintenance_interval_matrix(table.rows)
            or self.rule_evaluator.looks_like_maintenance_interval_table(
                headers, label_cells, direct_text
            )
            or self.rule_evaluator.looks_like_lubrication_schedule_table(
                headers, label_cells, direct_text, section_text
            )
        ):
            signals.add(TableSignal.MAINTENANCE_INTERVALS)
            signals.add(TableSignal.SCHEDULES)
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
            headers=headers, direct_text=direct_text
        ):
            signals.add(TableSignal.CONNECTIONS)
        if self.structured_list_classifier.looks_like_sensor_instrument_table(
            headers=headers, direct_text=direct_text
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
