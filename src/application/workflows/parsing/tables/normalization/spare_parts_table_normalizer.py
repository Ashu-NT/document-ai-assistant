from __future__ import annotations

from src.application.workflows.parsing.tables.rows.normalized_table_rows import (
    NormalizedTableRows,
)
from src.application.workflows.parsing.tables.normalization.spare_parts_normalization_support import (
    FIELD_LABELS,
    POSITION_WITH_DOT_PATTERN,
    QUANTITY_PATTERN,
    UNIT_PATTERN,
    apply_tail_code,
    header_fields,
    header_output_fields,
    looks_part_code,
    looks_position_token,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    looks_explicit_header_cell,
    normalize_cell,
)
from src.domain.assets.table_cell_span import TableCellSpan


class SparePartsTableNormalizer:
    def normalize(
        self,
        rows: list[list[str]],
        *,
        table_category: str | None,
        chunk_type: str | None,
        cell_spans: list[TableCellSpan] | None = None,
    ) -> NormalizedTableRows | None:
        if not self._should_normalize(
            table_category=table_category,
            chunk_type=chunk_type,
        ):
            return None

        parsed_rows: list[dict[str, str]] = []
        detected_header_fields: list[str] = []
        candidate_row_count = 0

        for row in rows:
            normalized_cells = [normalize_cell(cell) for cell in row if normalize_cell(cell)]
            if not normalized_cells:
                continue
            if self._looks_like_title_row(normalized_cells):
                continue
            if self._looks_like_header_row(normalized_cells):
                for field in header_fields(normalized_cells):
                    if field not in detected_header_fields:
                        detected_header_fields.append(field)
                continue

            candidate_row_count += 1
            parsed_rows.extend(self._parse_row(normalized_cells))

        if not parsed_rows:
            return None
        if candidate_row_count > 1 and len(parsed_rows) < 2:
            return None

        fields = header_output_fields(
            detected_header_fields=detected_header_fields,
            parsed_rows=parsed_rows,
        )
        normalized_rows = [
            [row.get(field, "") for field in fields]
            for row in parsed_rows
        ]
        return NormalizedTableRows(
            headers=[FIELD_LABELS[field] for field in fields],
            rows=normalized_rows,
        )

    @staticmethod
    def _should_normalize(
        *,
        table_category: str | None,
        chunk_type: str | None,
    ) -> bool:
        normalized_category = (table_category or "").strip().lower()
        if normalized_category == "spare_parts_table":
            return True
        return (chunk_type or "").strip().lower() == "spare_parts_table"

    @staticmethod
    def _looks_like_title_row(cells: list[str]) -> bool:
        if len(cells) != 1:
            return False
        normalized = cells[0].casefold()
        return normalized in {"spare parts list", "spare parts", "exploded views"}

    def _looks_like_header_row(self, cells: list[str]) -> bool:
        """Whether this row IS a header at all - kept separate from
        `_header_fields`'s marker mapping, which can legitimately come up
        empty for a recognized header row (e.g. "Reference | Code") that
        just doesn't use any of the known field vocabulary. Conflating
        the two previously let such header rows fall through and get
        miscounted as failed data rows, which could reject the whole
        table via the row-count guard below.

        A real position+quantity seed (e.g. "0020 4 Pce pin") overrides
        the header-keyword check - `looks_explicit_header_cell` matches
        several short, generic keywords ("pin", "wire", "tag", ...) that
        are common trailing words in genuine part descriptions, not just
        column headers.
        """
        if self._seed_tokens(cells) is not None:
            return False
        joined = " ".join(cells).casefold()
        return any(looks_explicit_header_cell(cell) for cell in cells) or "spare part" in joined

    def _parse_row(self, cells: list[str]) -> list[dict[str, str]]:
        explicit_row = self._parse_explicit_row(cells)
        if explicit_row is not None:
            return [explicit_row]

        joined = " ".join(cells).strip()
        if not joined:
            return []

        position_pairs = self._parse_position_pairs(joined)
        if position_pairs:
            return position_pairs

        free_form_row = self._parse_free_form_row(cells)
        if free_form_row is not None:
            return [free_form_row]

        reference_row = self._parse_reference_code_row(cells)
        if reference_row is not None:
            return [reference_row]

        return []

    def _parse_reference_code_row(self, cells: list[str]) -> dict[str, str] | None:
        """A plain two-column "description -> part code" lookup row with
        no position/quantity concept at all (e.g. a table headed
        "Reference | Code"), common for simple parts-reference lists.
        Only accepted for exactly two populated cells where the second
        looks like a real part code, so this doesn't swallow rows that
        belong to one of the more specific position-led shapes above.
        """
        if len(cells) != 2:
            return None
        description, code = cells[0].strip(), cells[1].strip()
        if not description or not code:
            return None
        if looks_position_token(description):
            return None
        if not looks_part_code(code):
            return None
        return {"description": description, "part_no": code}

    def _parse_explicit_row(self, cells: list[str]) -> dict[str, str] | None:
        seed = self._seed_tokens(cells)
        if seed is None:
            return None
        seed_index, tokens = seed

        row: dict[str, str] = {
            "position": tokens[0],
            "quantity": tokens[1],
        }
        description_parts: list[str] = []

        remainder_start = 2
        if len(tokens) > 2 and UNIT_PATTERN.match(tokens[2]):
            row["unit"] = tokens[2]
            remainder_start = 3
        if len(tokens) > remainder_start:
            description_parts.append(" ".join(tokens[remainder_start:]))

        for offset, cell in enumerate(cells[seed_index + 1 :], start=1):
            if not cell:
                continue
            if (
                "unit" not in row
                and len(cell.split()) == 1
                and UNIT_PATTERN.match(cell)
            ):
                row["unit"] = cell
                continue
            if offset == 1 and not looks_part_code(cell):
                description_parts.append(cell)
                continue
            snapshot = dict(row)
            apply_tail_code(row, cell)
            if row == snapshot and not looks_part_code(cell):
                description_parts.append(cell)
        description = " ".join(part.strip() for part in description_parts if part.strip()).strip()
        if description:
            row["description"] = description

        if row.get("description") or row.get("part_no"):
            return row
        return None

    def _seed_tokens(self, cells: list[str]) -> tuple[int, list[str]] | None:
        for index, cell in enumerate(cells):
            tokens = cell.split()
            if len(tokens) < 2:
                continue
            if not looks_position_token(tokens[0]):
                continue
            if not QUANTITY_PATTERN.match(tokens[1]):
                continue
            return index, tokens
        return None

    def _parse_free_form_row(self, cells: list[str]) -> dict[str, str] | None:
        joined = " ".join(cells).strip()
        tokens = joined.split()
        if len(tokens) < 3:
            return None
        if not looks_position_token(tokens[0]) or not QUANTITY_PATTERN.match(tokens[1]):
            return None

        row: dict[str, str] = {
            "position": tokens[0],
            "quantity": tokens[1],
        }
        description_start = 2
        if len(tokens) > 2 and UNIT_PATTERN.match(tokens[2]):
            row["unit"] = tokens[2]
            description_start = 3

        description_tokens = tokens[description_start:]
        trailing_cell = cells[-1].strip() if cells else ""
        if (
            len(description_tokens) >= 2
            and looks_part_code(trailing_cell)
            and trailing_cell == description_tokens[-1]
        ):
            row["part_no"] = trailing_cell
            description_tokens = description_tokens[:-1]

        description = " ".join(description_tokens).strip()
        if not description:
            return None
        row["description"] = description
        return row

    def _parse_position_pairs(self, value: str) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for match in POSITION_WITH_DOT_PATTERN.finditer(value):
            description = match.group("description").strip(" ,;:-")
            if not description:
                continue
            rows.append(
                {
                    "position": match.group("position"),
                    "description": description,
                }
            )
        return rows
