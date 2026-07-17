from dataclasses import dataclass

from src.domain.common import BoundingBox


@dataclass(slots=True)
class TableParallelStream:
    stream_index: int
    source_row_start: int
    source_row_end: int
    source_col_start: int
    source_col_end: int
    row_count: int
    column_count: int
    page_number: int | None = None
    center_x: float | None = None
    bbox: BoundingBox | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "stream_index": self.stream_index,
            "source_row_start": self.source_row_start,
            "source_row_end": self.source_row_end,
            "source_col_start": self.source_col_start,
            "source_col_end": self.source_col_end,
            "row_count": self.row_count,
            "column_count": self.column_count,
        }
        if self.page_number is not None:
            payload["page_number"] = self.page_number
        if self.center_x is not None:
            payload["center_x"] = self.center_x
        if self.bbox is not None:
            payload["bbox"] = {
                "x1": self.bbox.x1,
                "y1": self.bbox.y1,
                "x2": self.bbox.x2,
                "y2": self.bbox.y2,
            }
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TableParallelStream":
        bbox = data.get("bbox")
        return cls(
            stream_index=int(data.get("stream_index", 0)),
            source_row_start=int(data.get("source_row_start", 0)),
            source_row_end=int(data.get("source_row_end", 0)),
            source_col_start=int(data.get("source_col_start", 0)),
            source_col_end=int(data.get("source_col_end", 0)),
            row_count=int(data.get("row_count", 0)),
            column_count=int(data.get("column_count", 0)),
            page_number=(
                int(data["page_number"])
                if data.get("page_number") is not None
                else None
            ),
            center_x=(
                float(data["center_x"])
                if data.get("center_x") is not None
                else None
            ),
            bbox=cls._bbox_from_data(bbox),
        )

    @classmethod
    def list_from_data(
        cls,
        data: object,
    ) -> list["TableParallelStream"]:
        if not isinstance(data, list):
            return []
        return [cls.from_dict(item) for item in data if isinstance(item, dict)]

    @staticmethod
    def _bbox_from_data(value: object) -> BoundingBox | None:
        if not isinstance(value, dict):
            return None
        try:
            return BoundingBox(
                x1=float(value["x1"]),
                y1=float(value["y1"]),
                x2=float(value["x2"]),
                y2=float(value["y2"]),
            )
        except (KeyError, TypeError, ValueError):
            return None
