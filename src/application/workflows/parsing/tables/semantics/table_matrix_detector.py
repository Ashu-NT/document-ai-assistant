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
        interval_header_count = sum(
            1
            for header in headers[1:]
            if self.interval_expression_parser.is_interval_expression(header)
        )
        if interval_header_count < 2:
            return False

        body_rows = rows[1:]
        marker_like_cells = 0
        inspected_cells = 0
        for row in body_rows:
            for cell in row[1:]:
                inspected_cells += 1
                if self.boolean_marker_detector.is_boolean_marker(str(cell or "")):
                    marker_like_cells += 1

        if inspected_cells == 0:
            return False

        return marker_like_cells / inspected_cells >= 0.6
