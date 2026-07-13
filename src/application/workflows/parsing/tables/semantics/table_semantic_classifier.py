from src.application.workflows.parsing.tables.semantics.table_category import (
    TableCategory,
)
from src.application.workflows.parsing.tables.semantics.table_matrix_detector import (
    TableMatrixDetector,
)
from src.domain.assets import TableAsset


class TableSemanticClassifier:
    def __init__(
        self,
        *,
        matrix_detector: TableMatrixDetector | None = None,
    ) -> None:
        self.matrix_detector = matrix_detector or TableMatrixDetector()

    def classify(
        self,
        *,
        table: TableAsset,
        caption: str | None = None,
        section_path: list[str] | None = None,
        item_label: str | None = None,
    ) -> tuple[TableCategory, float]:
        headers = [str(cell or "").strip().casefold() for cell in (table.rows[0] if table.rows else [])]
        header_text = " | ".join(header for header in headers if header)
        section_text = " > ".join(section_path or []).casefold()
        caption_text = (caption or "").casefold()
        combined = " ".join(
            part for part in [header_text, caption_text, section_text, table.markdown.casefold()] if part
        )

        if item_label == "document_index" or "table of contents" in combined or "contents" in caption_text:
            return TableCategory.TOC_TABLE, 0.99
        if any(marker in combined for marker in ("spare part", "part number", "denomination", "qty")):
            return TableCategory.SPARE_PARTS_TABLE, 0.95
        if self.matrix_detector.is_maintenance_interval_matrix(table.rows):
            return TableCategory.MAINTENANCE_INTERVAL_TABLE, 0.92
        if self._looks_like_troubleshooting_table(headers, combined):
            return TableCategory.TROUBLESHOOTING_TABLE, 0.9
        if self._looks_like_operating_limits_table(headers, combined):
            return TableCategory.OPERATING_LIMITS_TABLE, 0.86
        if self._looks_like_technical_data_table(headers, combined):
            return TableCategory.TECHNICAL_DATA_TABLE, 0.84
        if self._looks_like_certification_table(headers, combined):
            return TableCategory.CERTIFICATION_TABLE, 0.82
        if self._looks_like_connection_table(headers, combined):
            return TableCategory.CONNECTION_TABLE, 0.8
        if self._looks_like_sensor_instrument_table(headers, combined):
            return TableCategory.SENSOR_INSTRUMENT_TABLE, 0.78
        if self._looks_like_identifier_table(headers, combined):
            return TableCategory.IDENTIFIER_TABLE, 0.76
        return TableCategory.GENERAL_TABLE, 0.4

    @staticmethod
    def _looks_like_troubleshooting_table(headers: list[str], combined: str) -> bool:
        troubleshooting_markers = ("fault", "symptom", "cause", "remedy", "action")
        return sum(marker in combined for marker in troubleshooting_markers) >= 2 and any(
            marker in " ".join(headers) for marker in troubleshooting_markers
        )

    @staticmethod
    def _looks_like_operating_limits_table(headers: list[str], combined: str) -> bool:
        markers = ("operating limit", "pressure", "temperature", "range")
        return sum(marker in combined for marker in markers) >= 2 and any(
            marker in " ".join(headers) for marker in ("pressure", "temperature", "limit")
        )

    @staticmethod
    def _looks_like_technical_data_table(headers: list[str], combined: str) -> bool:
        technical_markers = (
            "parameter",
            "value",
            "specification",
            "voltage",
            "power",
            "dimension",
            "capacity",
            "material",
        )
        return sum(marker in combined for marker in technical_markers) >= 2 and any(
            header in {"parameter", "value", "description", "specification"}
            for header in headers
        )

    @staticmethod
    def _looks_like_certification_table(headers: list[str], combined: str) -> bool:
        markers = ("certificate", "particulars", "approval", "conformity", "class")
        return sum(marker in combined for marker in markers) >= 2

    @staticmethod
    def _looks_like_identifier_table(headers: list[str], combined: str) -> bool:
        markers = ("serial number", "part number", "tag", "model", "code")
        return sum(marker in combined for marker in markers) >= 2

    @staticmethod
    def _looks_like_connection_table(headers: list[str], combined: str) -> bool:
        markers = ("terminal", "connection", "wire", "signal", "pin")
        return sum(marker in combined for marker in markers) >= 2

    @staticmethod
    def _looks_like_sensor_instrument_table(headers: list[str], combined: str) -> bool:
        markers = ("sensor", "instrument", "tag no", "tag number", "io", "p&id")
        return sum(marker in combined for marker in markers) >= 2
