from src.application.workflows.parsing.tables.semantics.table_category import (
    TableCategory,
)
from src.application.workflows.parsing.tables.semantics.table_matrix_detector import (
    TableMatrixDetector,
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
    ) -> None:
        self.matrix_detector = matrix_detector or TableMatrixDetector()
        self.row_canonicalizer = row_canonicalizer or TableRowCanonicalizer()

    def classify(
        self,
        *,
        table: TableAsset,
        caption: str | None = None,
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
        label_text = " ".join(label_cells)
        header_text = " | ".join(header for header in headers if header)
        direct_text = " ".join(
            part
            for part in [
                header_text,
                label_text,
                (caption or "").casefold(),
                table.markdown.casefold(),
            ]
            if part
        )
        section_text = " > ".join(section_path or []).casefold()
        fallback_text = " ".join(part for part in [direct_text, section_text] if part)

        if item_label == "document_index" or "table of contents" in fallback_text or "contents" in fallback_text:
            return TableCategory.TOC_TABLE, 0.99

        if self.matrix_detector.is_maintenance_interval_matrix(table.rows):
            return TableCategory.MAINTENANCE_INTERVAL_TABLE, 0.92
        if self._looks_like_maintenance_interval_table(headers, label_cells, direct_text):
            return TableCategory.MAINTENANCE_INTERVAL_TABLE, 0.89
        if self._looks_like_troubleshooting_table(headers, direct_text):
            return TableCategory.TROUBLESHOOTING_TABLE, 0.9
        if self._looks_like_spare_parts_table(headers, label_cells, direct_text):
            return TableCategory.SPARE_PARTS_TABLE, 0.9
        if self._looks_like_operating_limits_table(headers, label_cells, direct_text):
            return TableCategory.OPERATING_LIMITS_TABLE, 0.86
        if self._looks_like_technical_data_table(headers, label_cells, direct_text):
            return TableCategory.TECHNICAL_DATA_TABLE, 0.88
        if self._looks_like_certification_table(headers, direct_text, section_text):
            return TableCategory.CERTIFICATION_TABLE, 0.82
        if self._looks_like_connection_table(headers, direct_text):
            return TableCategory.CONNECTION_TABLE, 0.8
        if self._looks_like_sensor_instrument_table(headers, direct_text):
            return TableCategory.SENSOR_INSTRUMENT_TABLE, 0.78
        if self._looks_like_identifier_table(headers, label_cells, direct_text):
            return TableCategory.IDENTIFIER_TABLE, 0.76
        return TableCategory.GENERAL_TABLE, 0.4

    @staticmethod
    def _looks_like_maintenance_interval_table(
        headers: list[str],
        labels: list[str],
        direct_text: str,
    ) -> bool:
        header_text = " ".join(headers)
        label_text = " ".join(labels)
        interval_markers = ("interval", "service interval", "maintenance interval", "frequency", "period")
        maintenance_markers = ("maintenance", "inspect", "clean", "replace", "lubric", "check")
        has_interval_header = any(marker in header_text for marker in interval_markers)
        has_maintenance_header = any(marker in header_text for marker in maintenance_markers)
        has_interval_body = any(marker in direct_text for marker in interval_markers) or any(
            token in direct_text for token in ("daily", "weekly", "monthly", "quarterly", "yearly", "hours")
        )
        has_maintenance_body = any(marker in label_text or marker in direct_text for marker in maintenance_markers)
        return (has_interval_header and has_maintenance_body) or (has_maintenance_header and has_interval_body)

    @staticmethod
    def _looks_like_troubleshooting_table(headers: list[str], direct_text: str) -> bool:
        header_text = " ".join(headers)
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
        return sum(marker in direct_text for marker in troubleshooting_markers) >= 2 and any(
            marker in header_text for marker in troubleshooting_markers
        )

    @staticmethod
    def _looks_like_spare_parts_table(
        headers: list[str],
        labels: list[str],
        direct_text: str,
    ) -> bool:
        header_text = " ".join(headers)
        label_text = " ".join(labels)
        spare_part_markers = (
            "spare part",
            "part number",
            "part no",
            "denomination",
            "qty",
            "quantity",
            "position",
            "service package",
        )
        return sum(marker in direct_text for marker in spare_part_markers) >= 2 and (
            any(marker in header_text for marker in spare_part_markers)
            or any(marker in label_text for marker in ("position", "part", "service package"))
        )

    @staticmethod
    def _looks_like_operating_limits_table(
        headers: list[str],
        labels: list[str],
        direct_text: str,
    ) -> bool:
        header_text = " ".join(headers)
        label_text = " ".join(labels)
        markers = ("operating limit", "pressure", "temperature", "range")
        return sum(marker in direct_text for marker in markers) >= 2 and any(
            marker in header_text or marker in label_text
            for marker in ("pressure", "temperature", "limit", "range")
        )

    @staticmethod
    def _looks_like_technical_data_table(
        headers: list[str],
        labels: list[str],
        direct_text: str,
    ) -> bool:
        header_text = " ".join(headers)
        label_text = " ".join(labels)
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
        direct_hits = sum(marker in direct_text for marker in technical_markers)
        label_hits = sum(marker in label_text for marker in technical_markers)
        has_explicit_header = any(
            header in {"parameter", "value", "description", "specification"}
            for header in headers
        )
        return direct_hits >= 2 and (has_explicit_header or label_hits >= 2 or "technical data" in header_text)

    @staticmethod
    def _looks_like_certification_table(
        headers: list[str],
        direct_text: str,
        section_text: str,
    ) -> bool:
        markers = ("certificate", "particulars", "approval", "conformity", "class")
        return sum(marker in direct_text for marker in markers) >= 2 or (
            "certificate" in section_text and sum(marker in direct_text for marker in ("approval", "class", "particulars")) >= 1
        )

    @staticmethod
    def _looks_like_identifier_table(
        headers: list[str],
        labels: list[str],
        direct_text: str,
    ) -> bool:
        header_text = " ".join(headers)
        label_text = " ".join(labels)
        markers = ("serial number", "part number", "tag", "model", "code")
        return sum(marker in label_text or marker in direct_text for marker in markers) >= 2 and not any(
            technical_marker in label_text or technical_marker in header_text
            for technical_marker in ("voltage", "power", "pressure", "temperature", "capacity")
        )

    @staticmethod
    def _looks_like_connection_table(headers: list[str], direct_text: str) -> bool:
        markers = ("terminal", "connection", "wire", "signal", "pin")
        return sum(marker in direct_text for marker in markers) >= 2

    @staticmethod
    def _looks_like_sensor_instrument_table(headers: list[str], direct_text: str) -> bool:
        markers = ("sensor", "instrument", "tag no", "tag number", "io", "p&id")
        return sum(marker in direct_text for marker in markers) >= 2

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
