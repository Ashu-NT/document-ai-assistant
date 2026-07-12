from dataclasses import dataclass, field

from src.domain.assets.asset_metadata import AssetMetadata
from src.domain.common import AuditMetadata


@dataclass(slots=True)
class TableAsset:
    table_id: str
    document_id: str

    markdown: str

    parent_section_id: str | None = None

    rows: list[list[str]] = field(default_factory=list)
    row_count: int | None = None
    column_count: int | None = None

    metadata: AssetMetadata = field(default_factory=AssetMetadata)
    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def has_content(self) -> bool:
        return bool(self.markdown and self.markdown.strip())

    def has_structured_rows(self) -> bool:
        return bool(self.rows)

    def to_embedding_text(self) -> str:
        parts = []

        if self.metadata.caption:
            parts.append(f"Table Caption: {self.metadata.caption}")

        parts.append(self.markdown)

        return "\n".join(parts)

    def to_structured_row_text(self) -> str | None:
        """Renders each body row as an explicit `header=value` line, using the
        first row as column labels. Meant to be appended alongside
        `to_embedding_text()` -- not a replacement -- so a consumer (LLM
        extraction, QA evidence) has an unambiguous, row-by-row echo of the
        table to cross-check against the markdown, rather than having to
        visually re-parse pipe-delimited text itself."""
        if len(self.rows) < 2:
            return None

        headers = self._structured_row_headers()
        if headers is None:
            return None
        lines = []
        for row_index, row in enumerate(self.rows[1:], start=1):
            cells = [
                f"{headers[column_index].strip()}={cell.strip()}"
                for column_index, cell in enumerate(row)
                if column_index < len(headers)
                and headers[column_index].strip()
                and cell.strip()
            ]
            if cells:
                lines.append(f"Row {row_index}: " + " | ".join(cells))

        if not lines:
            return None

        return "\n".join(lines)

    def _structured_row_headers(self) -> list[str] | None:
        headers = [" ".join(str(cell or "").split()).strip() for cell in self.rows[0]]
        if len(headers) < 2 or any(not header for header in headers):
            return None
        lowered = [header.lower() for header in headers]
        if len(set(lowered)) != len(lowered):
            return None
        if any(_looks_schedule_marker_header(header) for header in headers):
            return None
        numeric_like = sum(1 for header in headers if _looks_numeric(header))
        if numeric_like >= max(1, len(headers) // 2):
            return None
        return headers


def _looks_numeric(value: str) -> bool:
    stripped = value.strip().replace(",", "").replace(".", "").replace("-", "")
    return bool(stripped) and stripped.isdigit()


def _looks_schedule_marker_header(value: str) -> bool:
    tokens = [token.strip().lower() for token in value.split() if token.strip()]
    if not tokens:
        return False
    schedule_codes = {"d", "w", "m", "q", "s", "a"}
    return all(token in schedule_codes for token in tokens)
