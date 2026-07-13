from dataclasses import dataclass, field


@dataclass(slots=True)
class TableCellSpan:
    row_start: int
    row_end: int
    col_start: int
    col_end: int
    text: str
    normalized_text: str | None = None
    raw_lines: list[str] = field(default_factory=list)

    @property
    def row_span(self) -> int:
        return max(1, self.row_end - self.row_start + 1)

    @property
    def col_span(self) -> int:
        return max(1, self.col_end - self.col_start + 1)

    def to_dict(self) -> dict[str, object]:
        return {
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

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TableCellSpan":
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
