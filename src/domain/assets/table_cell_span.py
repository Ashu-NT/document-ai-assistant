from dataclasses import dataclass, field

from src.domain.common import BoundingBox


@dataclass(slots=True)
class TableCellSpan:
    row_start: int
    row_end: int
    col_start: int
    col_end: int
    text: str
    normalized_text: str | None = None
    raw_lines: list[str] = field(default_factory=list)
    page_number: int | None = None
    bbox: BoundingBox | None = None

    @property
    def row_span(self) -> int:
        return max(1, self.row_end - self.row_start + 1)

    @property
    def col_span(self) -> int:
        return max(1, self.col_end - self.col_start + 1)

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "row_start": self.row_start,
            "row_end": self.row_end,
            "col_start": self.col_start,
            "col_end": self.col_end,
            "row_span": self.row_span,
            "col_span": self.col_span,
            "text": self.text,
            "normalized_text": self.normalized_text,
            "raw_lines": list(self.raw_lines),
        }
        if self.page_number is not None:
            payload["page_number"] = self.page_number
        if self.bbox is not None:
            payload["bbox"] = {
                "x1": self.bbox.x1,
                "y1": self.bbox.y1,
                "x2": self.bbox.x2,
                "y2": self.bbox.y2,
            }
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TableCellSpan":
        bbox = data.get("bbox")
        return cls(
            row_start=int(data.get("row_start", 0)),
            row_end=int(data.get("row_end", data.get("row_start", 0))),
            col_start=int(data.get("col_start", 0)),
            col_end=int(data.get("col_end", data.get("col_start", 0))),
            text=str(data.get("text") or ""),
            normalized_text=(
                str(data["normalized_text"])
                if data.get("normalized_text") is not None
                else None
            ),
            raw_lines=[
                str(line)
                for line in (data.get("raw_lines") or [])
                if str(line).strip()
            ],
            page_number=(
                int(data["page_number"])
                if data.get("page_number") is not None
                else None
            ),
            bbox=cls._bbox_from_data(bbox),
        )

    @classmethod
    def list_from_data(
        cls,
        data: object,
    ) -> list["TableCellSpan"]:
        if not isinstance(data, list):
            return []
        return [
            cls.from_dict(item)
            for item in data
            if isinstance(item, dict)
        ]

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
