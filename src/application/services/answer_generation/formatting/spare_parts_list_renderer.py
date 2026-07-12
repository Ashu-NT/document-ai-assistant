from __future__ import annotations

from typing import Sequence

from src.application.services.answer_generation.formatting.spare_parts.spare_parts_group import (
    SparePartsGroup,
)
from src.application.services.answer_generation.formatting.spare_parts_table_evidence_detector import (
    has_table_evidence,
)
from src.application.services.answer_generation.formatting.spare_parts_table_parser import (
    SPARE_PARTS_TABLE_PARSER_RULES_VERSION,
    SparePartsTableParser,
)
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
)
from src.domain.common import ChunkType
from src.shared.text.ascii_table_renderer import AsciiTableColumn, render_ascii_table

_SUPPORTED_INTENTS = {AnswerIntent.TABLE_SUMMARY, AnswerIntent.IDENTIFIER_LOOKUP}
_PARTIAL_CONTENT_NOTICE = (
    "Only partial row content was available in the retrieved context."
)
_EXPORT_FORMAT_MARKERS = ("markdown", "csv", "export", "spreadsheet", ".csv", ".md")
_SPARE_PARTS_REQUEST_MARKERS = ("spare part", "spare parts")
_ROW_FIELD_LABELS: dict[str, str] = {
    "position": "Position",
    "pid_position": "P&ID Position",
    "quantity": "Quantity",
    "unit": "Unit",
    "service": "Service",
    "type": "Type",
    "description": "Description",
    "part_no": "Part No.",
    "service_package": "Service package",
    "component": "Component",
    "manufacturer": "Manufacturer",
}
_ROW_FIELD_ORDER = (
    "position",
    "pid_position",
    "quantity",
    "unit",
    "service",
    "type",
    "description",
    "part_no",
    "service_package",
    "component",
    "manufacturer",
)
_ROW_FIELD_MAX_WIDTHS: dict[str, int] = {
    "position": 14,
    "pid_position": 18,
    "quantity": 10,
    "unit": 8,
    "service": 26,
    "type": 36,
    "description": 34,
    "part_no": 18,
    "service_package": 18,
    "component": 24,
    "manufacturer": 24,
}

_STRUCTURED_ENTITY_TYPE = "spare_part"
_STRUCTURED_GROUP_TITLE = "Spare Parts (from extracted data)"


class SparePartsListRenderer:
    """Deterministically renders a spare-parts answer, bypassing the LLM,
    when the question and intent both indicate a spare-parts list request.

    Prefers spare-part rows already extracted into structured DB tables
    during ingestion (`resolved_structured_entities`) as the single source
    of truth. Only falls back to regex-parsing raw source text (via
    `SparePartsTableParser`) when no structured extraction is available for
    this document/query -- avoiding both the redundant parsing work and the
    risk of the two sources disagreeing on the same document.

    Consumes `AnswerSource` (from `StructuredAnswerContext.sources`) rather
    than raw `RetrievedChunk`s -- `AnswerSource.table_rows` is already
    decoded once by `StructuredSourceBuilder`, so `SparePartsTableParser`
    doesn't need its own second `table_rows_json` decode of the same chunk
    metadata (plan section 4.7/9.5).
    """

    def __init__(self, *, table_parser: SparePartsTableParser | None = None) -> None:
        self._table_parser = table_parser or SparePartsTableParser()
        self._last_dropped_row_count = 0
        self._last_partial = False

    def render(
        self,
        *,
        question: str,
        answer_intent: AnswerIntent | None,
        sources: Sequence[AnswerSource],
        resolved_structured_entities: Sequence[dict] = (),
    ) -> str | None:
        self._last_dropped_row_count = 0
        self._last_partial = False
        if answer_intent not in _SUPPORTED_INTENTS:
            return None
        if not self._looks_like_spare_parts_request(question):
            return None
        if self._wants_export_format(question):
            return None

        structured_group = self._build_group_from_structured_entities(
            resolved_structured_entities
        )
        if structured_group is not None:
            return self._render_groups([structured_group])

        groups: list[SparePartsGroup] = []
        for source in sources:
            if source.chunk_type != ChunkType.SPARE_PARTS_TABLE.value:
                continue
            if not has_table_evidence(source):
                continue
            groups.append(self._table_parser.build_group(source))
        if not groups:
            return None

        self._last_dropped_row_count = sum(group.dropped_row_count for group in groups)
        self._last_partial = any(group.partial for group in groups)
        return self._render_groups(groups)

    def last_diagnostics(self) -> dict[str, object]:
        """Diagnostics from the most recent render() call, so a caller can
        measure whether SparePartsTableParser's row-parsing quality
        improves, regresses, or only changes shape across future phases,
        instead of that signal only ever reaching the user as the one-line
        `_PARTIAL_CONTENT_NOTICE` inside the rendered text. Only meaningful
        after a render() call that took the chunk-parsing path -- the
        structured-entity path and every early-return path leave the drop
        count at 0 and partial at False, since SparePartsTableParser was
        not exercised in those cases."""
        return {
            "spare_parts_table_parser_rules_version": SPARE_PARTS_TABLE_PARSER_RULES_VERSION,
            "spare_parts_dropped_row_count": self._last_dropped_row_count,
            "spare_parts_partial": self._last_partial,
        }

    @staticmethod
    def _looks_like_spare_parts_request(question: str) -> bool:
        normalized = " ".join((question or "").strip().lower().split())
        return any(marker in normalized for marker in _SPARE_PARTS_REQUEST_MARKERS)

    @staticmethod
    def _wants_export_format(question: str) -> bool:
        normalized = (question or "").strip().lower()
        return any(marker in normalized for marker in _EXPORT_FORMAT_MARKERS)

    # -- structured-entity source (preferred over regex chunk parsing) -------

    def _build_group_from_structured_entities(
        self,
        entities: Sequence[dict],
    ) -> SparePartsGroup | None:
        rows: list[dict[str, str]] = []
        for entity in entities:
            if not isinstance(entity, dict):
                continue
            if entity.get("_entity_type") != _STRUCTURED_ENTITY_TYPE:
                continue
            row = self._row_from_structured_entity(entity)
            if row is not None:
                rows.append(row)
        if not rows:
            return None
        return SparePartsGroup(
            section_title=_STRUCTURED_GROUP_TITLE,
            section_path=None,
            page_start=None,
            page_end=None,
            rows=rows,
            raw_rows=[],
            partial=False,
        )

    @staticmethod
    def _row_from_structured_entity(entity: dict) -> dict[str, str] | None:
        row: dict[str, str] = {}
        for entity_field, row_field in (
            ("part_number", "part_no"),
            ("description", "description"),
            ("quantity", "quantity"),
            ("component_name", "component"),
            ("manufacturer_name", "manufacturer"),
        ):
            value = entity.get(entity_field)
            if value is not None and str(value).strip():
                row[row_field] = str(value).strip()
        if "part_no" not in row and "description" not in row:
            return None
        return row

    # -- rendering -----------------------------------------------------------

    def _render_groups(self, groups: Sequence[SparePartsGroup]) -> str:
        lines = ["Spare parts lists found:", ""]
        for index, group in enumerate(groups, start=1):
            lines.append(f"{index}. {group.section_title}")
            lines.append(
                f"   Pages: {self._page_range(group.page_start, group.page_end)}"
            )
            lines.append(f"   Section: {group.section_path or '-'}")
            lines.append("   Type: spare_parts_table")
            lines.append("")
            if group.rows:
                lines.append("   Available rows:")
                lines.extend(self._indented_table_lines(group.rows))
            for raw_row in group.raw_rows:
                lines.append(f"   - Raw row: {raw_row}")
            if group.partial:
                lines.append(f"   {_PARTIAL_CONTENT_NOTICE}")
            if index < len(groups):
                lines.append("")
        return "\n".join(lines).strip()

    @staticmethod
    def _indented_table_lines(rows: Sequence[dict[str, str]]) -> list[str]:
        columns = [
            AsciiTableColumn(
                key=field,
                title=_ROW_FIELD_LABELS[field],
                max_width=_ROW_FIELD_MAX_WIDTHS[field],
            )
            for field in _visible_row_fields(rows)
        ]
        if not columns:
            return []
        table_text = render_ascii_table(columns=columns, rows=rows)
        return [f"   {line}" for line in table_text.splitlines()]

    @staticmethod
    def _page_range(page_start: int | None, page_end: int | None) -> str:
        if page_start is None and page_end is None:
            return "-"
        if page_end is None or page_end == page_start:
            return str(page_start)
        return f"{page_start}-{page_end}"


def _visible_row_fields(rows: Sequence[dict[str, str]]) -> list[str]:
    visible_fields: list[str] = []
    for field in _ROW_FIELD_ORDER:
        if any(str(row.get(field, "")).strip() for row in rows):
            visible_fields.append(field)
    return visible_fields
