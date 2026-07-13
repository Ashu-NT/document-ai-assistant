from src.application.workflows.parsing.tables.semantics.table_category import (
    TableCategory,
)
from src.application.workflows.parsing.tables.semantics.table_matrix_detector import (
    TableMatrixDetector,
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
    ) -> None:
        self.matrix_detector = matrix_detector or TableMatrixDetector()
        self.row_canonicalizer = row_canonicalizer or TableRowCanonicalizer()
        self.signal_matcher = signal_matcher or TableTextSignalMatcher()
        self.structured_list_classifier = (
            structured_list_classifier
            or TableStructuredListClassifier(signal_matcher=self.signal_matcher)
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
        label_cells = self._body_label_cells(body_rows, has_header_row=has_header_row)
        label_text = self.signal_matcher.normalized_text(*label_cells)
        header_text = self.signal_matcher.normalized_text(*headers)
        direct_text = self.signal_matcher.normalized_text(
            header_text,
            label_text,
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
        if self._looks_like_maintenance_interval_table(headers, label_cells, direct_text):
            return TableCategory.MAINTENANCE_INTERVAL_TABLE, 0.89
        if self._looks_like_troubleshooting_table(headers, direct_text):
            return TableCategory.TROUBLESHOOTING_TABLE, 0.9
        if self.structured_list_classifier.looks_like_spare_parts_table(
            headers=headers,
            labels=label_cells,
            body_rows=body_rows,
            direct_text=direct_text,
            section_text=section_text,
        ):
            return TableCategory.SPARE_PARTS_TABLE, 0.9
        if self._looks_like_operating_limits_table(headers, label_cells, direct_text):
            return TableCategory.OPERATING_LIMITS_TABLE, 0.86
        if self._looks_like_technical_data_table(headers, label_cells, direct_text):
            return TableCategory.TECHNICAL_DATA_TABLE, 0.88
        if self._looks_like_certification_table(headers, direct_text, section_text):
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
        ):
            return TableCategory.IDENTIFIER_TABLE, 0.76
        return TableCategory.GENERAL_TABLE, 0.4

    def _looks_like_maintenance_interval_table(
        self,
        headers: list[str],
        labels: list[str],
        direct_text: str,
    ) -> bool:
        interval_markers = ("interval", "service interval", "maintenance interval", "frequency", "period")
        temporal_markers = (
            "daily",
            "weekly",
            "monthly",
            "quarterly",
            "yearly",
            "year",
            "month",
            "months",
            "hour",
            "hours",
            "every",
            "when needed",
        )
        maintenance_markers = ("maintenance", "inspect", "clean", "replace", "lubric", "check")
        interval_header_count = self.signal_matcher.count_interval_header_tokens(headers)
        header_text = self.signal_matcher.normalized_text(*headers)
        label_text = self.signal_matcher.normalized_text(*labels)
        interval_hits = self.signal_matcher.count_unique(direct_text, interval_markers)
        temporal_hits = self.signal_matcher.count_unique(direct_text, temporal_markers)
        maintenance_hits = self.signal_matcher.count_unique(
            self.signal_matcher.normalized_text(label_text, direct_text),
            maintenance_markers,
        )
        return (
            interval_header_count >= 2 and maintenance_hits >= 1
        ) or (
            self.signal_matcher.count_unique(header_text, interval_markers) >= 1
            and maintenance_hits >= 1
            and (interval_hits >= 1 or temporal_hits >= 2)
        )

    def _looks_like_troubleshooting_table(self, headers: list[str], direct_text: str) -> bool:
        header_text = self.signal_matcher.normalized_text(*headers)
        troubleshooting_markers = (
            "fault",
            "problem",
            "symptom",
            "cause",
            "causes",
            "remedy",
            "remedies",
            "corrective action",
        )
        return (
            self.signal_matcher.count_unique(direct_text, troubleshooting_markers) >= 3
            and self.signal_matcher.count_unique(header_text, troubleshooting_markers) >= 2
        )

    def _looks_like_operating_limits_table(
        self,
        headers: list[str],
        labels: list[str],
        direct_text: str,
    ) -> bool:
        header_text = self.signal_matcher.normalized_text(*headers)
        label_text = self.signal_matcher.normalized_text(*labels)
        markers = ("operating limit", "pressure", "temperature", "range")
        return self.signal_matcher.count_unique(direct_text, markers) >= 2 and any(
            self.signal_matcher.contains(header_text, marker)
            or self.signal_matcher.contains(label_text, marker)
            for marker in ("pressure", "temperature", "limit", "range")
        )

    def _looks_like_technical_data_table(
        self,
        headers: list[str],
        labels: list[str],
        direct_text: str,
    ) -> bool:
        header_text = self.signal_matcher.normalized_text(*headers)
        label_text = self.signal_matcher.normalized_text(*labels)
        technical_markers = (
            "capacity",
            "current",
            "dimension",
            "flow rate",
            "installed power",
            "material",
            "parameter",
            "power",
            "pressure",
            "pump type",
            "rpm",
            "serial number",
            "specification",
            "temperature",
            "value",
            "voltage",
            "weight",
            "year of manufacture",
        )
        direct_hits = self.signal_matcher.count_unique(direct_text, technical_markers)
        label_hits = self.signal_matcher.count_unique(label_text, technical_markers)
        has_explicit_header = any(
            header in {"parameter", "value", "description", "specification"}
            for header in headers
        )
        return direct_hits >= 2 and (
            has_explicit_header
            or label_hits >= 2
            or self.signal_matcher.contains(header_text, "technical data")
        )

    def _looks_like_certification_table(
        self,
        headers: list[str],
        direct_text: str,
        section_text: str,
    ) -> bool:
        markers = ("certificate", "particulars", "approval", "conformity", "class")
        return self.signal_matcher.count_unique(direct_text, markers) >= 2 or (
            self.signal_matcher.contains(section_text, "certificate")
            and self.signal_matcher.count_unique(
                direct_text,
                ("approval", "class", "particulars"),
            ) >= 1
        )

    @staticmethod
    def _body_label_cells(
        rows: list[list[str]],
        *,
        has_header_row: bool,
    ) -> list[str]:
        labels: list[str] = []
        for row in rows:
            non_empty = [str(cell or "").strip().casefold() for cell in row if str(cell or "").strip()]
            if len(non_empty) >= 2:
                labels.append(non_empty[0])
            elif not has_header_row and non_empty:
                labels.append(non_empty[0])
        return labels
