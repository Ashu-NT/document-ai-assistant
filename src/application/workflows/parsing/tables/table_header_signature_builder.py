import re

from src.domain.assets import TableAsset


class TableHeaderSignatureBuilder:
    def build(self, table: TableAsset) -> str | None:
        if not table.rows:
            return None

        header_row = table.rows[0]
        normalized_headers: list[str] = []
        for cell in header_row:
            normalized = self._normalize_cell(cell)
            if normalized:
                normalized_headers.append(normalized)
        if not normalized_headers:
            return None

        return "|".join(normalized_headers)

    @staticmethod
    def _normalize_cell(value: str | None) -> str:
        if not value:
            return ""

        text = value.casefold()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s/%.-]", "", text)
        return text.strip()
