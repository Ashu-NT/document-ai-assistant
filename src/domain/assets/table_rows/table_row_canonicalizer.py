from __future__ import annotations

from src.domain.assets.table_rows.table_row_patterns import (
    clean_rows,
    looks_explicit_header_cell,
    looks_label_cell,
    looks_numeric,
    normalize_cell,
)


class TableRowCanonicalizer:
    def canonicalize(self, rows: list[list[str]]) -> list[list[str]]:
        cleaned_rows = clean_rows(rows)
        if len(cleaned_rows) < 2:
            return cleaned_rows
        if self.has_explicit_header_row(cleaned_rows):
            return cleaned_rows
        key_value_rows = self._canonicalize_key_value_rows(cleaned_rows)
        if key_value_rows is not None:
            return key_value_rows
        transposed_rows = self._canonicalize_transposed_key_value_rows(cleaned_rows)
        if transposed_rows is not None:
            return transposed_rows
        return cleaned_rows

    def has_explicit_header_row(self, rows: list[list[str]]) -> bool:
        if len(rows) < 2:
            return False
        header = rows[0]
        non_empty = [normalize_cell(cell) for cell in header if normalize_cell(cell)]
        if len(non_empty) < 2:
            return False
        numeric_like = sum(1 for cell in non_empty if looks_numeric(cell))
        if numeric_like >= max(1, len(non_empty) // 2):
            return False
        return any(looks_explicit_header_cell(cell) for cell in non_empty)

    def _canonicalize_key_value_rows(
        self,
        rows: list[list[str]],
    ) -> list[list[str]] | None:
        canonical_pairs: list[list[str]] = []
        pair_row_count = 0

        for row in rows:
            non_empty = [normalize_cell(cell) for cell in row if normalize_cell(cell)]
            if len(non_empty) < 2 or len(non_empty) % 2 != 0:
                continue

            row_pairs: list[list[str]] = []
            for index in range(0, len(non_empty), 2):
                label = non_empty[index]
                value = non_empty[index + 1]
                if not looks_label_cell(label) or not value:
                    row_pairs = []
                    break
                row_pairs.append([label, value])

            if not row_pairs:
                continue

            pair_row_count += 1
            canonical_pairs.extend(row_pairs)

        if pair_row_count < max(2, len(rows) // 2):
            return None
        if len(canonical_pairs) < 2:
            return None
        return [["Label", "Value"], *canonical_pairs]

    def _canonicalize_transposed_key_value_rows(
        self,
        rows: list[list[str]],
    ) -> list[list[str]] | None:
        if len(rows) != 2:
            return None

        header_candidates = rows[0]
        value_candidates = rows[1]
        pairs: list[list[str]] = []
        for index, label in enumerate(header_candidates):
            if index >= len(value_candidates):
                continue
            cleaned_label = normalize_cell(label)
            cleaned_value = normalize_cell(value_candidates[index])
            if not cleaned_label or not cleaned_value:
                continue
            if not looks_label_cell(cleaned_label):
                return None
            pairs.append([cleaned_label, cleaned_value])

        if len(pairs) < 2:
            return None
        return [["Label", "Value"], *pairs]
