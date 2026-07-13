from src.application.workflows.parsing.tables.semantics.boolean_marker_detector import (
    BooleanMarkerDetector,
)
from src.application.workflows.parsing.tables.semantics.interval_expression_parser import (
    IntervalExpressionParser,
)


class TableMatrixDetector:
    def __init__(
        self,
        *,
        interval_expression_parser: IntervalExpressionParser | None = None,
        boolean_marker_detector: BooleanMarkerDetector | None = None,
    ) -> None:
        self.interval_expression_parser = (
            interval_expression_parser or IntervalExpressionParser()
        )
        self.boolean_marker_detector = (
            boolean_marker_detector or BooleanMarkerDetector()
        )

    def is_maintenance_interval_matrix(self, rows: list[list[str]]) -> bool:
        if len(rows) < 2 or len(rows[0]) < 3:
            return False

        headers = [str(cell or "").strip() for cell in rows[0]]
        interval_columns = {
            index
            for index, header in enumerate(headers)
            if self.interval_expression_parser.is_interval_expression(header)
        }
        interval_header_count = len(interval_columns)
        if interval_header_count < 2:
            return False

        body_rows = rows[1:]
        marker_like_cells = 0
        inspected_cells = 0
        descriptive_content_found = False
        for row in body_rows:
            for index, cell in enumerate(row):
                if index in interval_columns:
                    cleaned_cell = str(cell or "").strip()
                    if not cleaned_cell:
                        continue
                    inspected_cells += 1
                    if self.boolean_marker_detector.is_boolean_marker(cleaned_cell):
                        marker_like_cells += 1
                    continue
                if str(cell or "").strip():
                    descriptive_content_found = True

        if inspected_cells == 0 or not descriptive_content_found:
            return False

        return marker_like_cells / inspected_cells >= 0.45
