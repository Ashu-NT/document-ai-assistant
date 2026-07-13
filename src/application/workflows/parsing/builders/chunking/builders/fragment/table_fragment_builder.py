from src.application.workflows.parsing.builders.chunking.builders.fragment.asset_context_resolver import (
    AssetContextResolver,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
    resolve_parser_extra,
)
from src.application.workflows.parsing.parsing_value_coercion import (
    coerce_float,
    coerce_positive_int,
)
from src.domain.common import ChunkType
from src.domain.elements import CanonicalElement


class TableFragmentBuilder:
    """Builds fragment text and classifies chunk type for table elements."""

    def __init__(
        self,
        *,
        text_splitter: ChunkTextSplitter,
        include_table_context: bool,
        asset_context_resolver: AssetContextResolver,
    ) -> None:
        self.text_splitter = text_splitter
        self.include_table_context = include_table_context
        self.asset_context_resolver = asset_context_resolver

    def should_chunk_table_element(self, element: CanonicalElement) -> bool:
        parser_extra = resolve_parser_extra(element)
        column_count = coerce_positive_int(parser_extra.get("column_count"))
        row_count = coerce_positive_int(parser_extra.get("row_count"))
        markdown = clean_chunk_text(parser_extra.get("markdown") or element.text) or ""

        if column_count is not None and column_count <= 1:
            return False

        if (
            row_count is not None
            and row_count <= 1
            and self.text_splitter.count_tokens(markdown) > 30
        ):
            return False

        return True

    def table_fragment_text(
        self,
        *,
        elements: list[CanonicalElement],
        index: int,
        element: CanonicalElement,
    ) -> str | None:
        parser_extra = resolve_parser_extra(element)
        markdown = clean_chunk_text(parser_extra.get("markdown") or element.text)
        caption = clean_chunk_text(parser_extra.get("caption"))
        nearby_text = (
            self.asset_context_resolver.nearby_text(elements=elements, index=index)
            if self.include_table_context
            else None
        )

        parts = [part for part in [caption, nearby_text, markdown] if part]
        if not parts:
            return None

        return "\n\n".join(parts).strip()

    def table_context_text(
        self,
        *,
        elements: list[CanonicalElement],
        index: int,
        element: CanonicalElement,
    ) -> str | None:
        parser_extra = resolve_parser_extra(element)
        caption = clean_chunk_text(parser_extra.get("caption"))
        nearby_text = (
            self.asset_context_resolver.nearby_text(elements=elements, index=index)
            if self.include_table_context
            else None
        )
        parts = [part for part in [caption, nearby_text] if part]
        return "\n\n".join(parts).strip() if parts else None

    @staticmethod
    def table_markdown_text(element: CanonicalElement) -> str | None:
        parser_extra = resolve_parser_extra(element)
        return clean_chunk_text(parser_extra.get("markdown") or element.text)

    @staticmethod
    def compose_table_text(
        *,
        context_text: str | None,
        markdown_text: str | None,
    ) -> str | None:
        parts = [part for part in [context_text, markdown_text] if part]
        if not parts:
            return None
        return "\n\n".join(parts).strip()

    @staticmethod
    def table_rows(element: CanonicalElement) -> list[list[str]] | None:
        parser_extra = resolve_parser_extra(element)
        table_rows = parser_extra.get("table_rows")
        return table_rows if table_rows else None

    @staticmethod
    def table_metadata(element: CanonicalElement) -> dict[str, object]:
        parser_extra = resolve_parser_extra(element)
        return {
            "logical_table_family_id": str(
                parser_extra.get("logical_table_family_id") or ""
            ).strip()
            or None,
            "logical_table_family_index": coerce_positive_int(
                parser_extra.get("family_index")
            ),
            "logical_table_family_total": coerce_positive_int(
                parser_extra.get("family_total")
            ),
            "logical_table_continuation_role": str(
                parser_extra.get("continuation_role") or ""
            ).strip()
            or None,
            "table_category": str(parser_extra.get("table_category") or "").strip()
            or None,
            "table_category_confidence": coerce_float(
                parser_extra.get("table_category_confidence")
            ),
        }

    def table_chunk_type(
        self,
        element: CanonicalElement,
        text: str | None,
    ) -> ChunkType:
        parser_extra = resolve_parser_extra(element)
        table_category = str(parser_extra.get("table_category") or "").strip().lower()
        category_chunk_type = self._chunk_type_from_table_category(table_category)
        if category_chunk_type is not None:
            return category_chunk_type

        haystack = " ".join(
            part
            for part in [
                clean_chunk_text(parser_extra.get("caption")),
                clean_chunk_text(parser_extra.get("markdown")),
                text,
            ]
            if part
        ).lower()

        spare_part_markers = (
            "spare part",
            "spare parts",
            "part number",
            "part no",
            "| part |",
            "| part number |",
        )
        if any(marker in haystack for marker in spare_part_markers):
            return ChunkType.SPARE_PARTS_TABLE

        if self._has_spare_part_header_row(parser_extra):
            return ChunkType.SPARE_PARTS_TABLE

        return ChunkType.GENERAL

    @staticmethod
    def _chunk_type_from_table_category(table_category: str) -> ChunkType | None:
        if table_category == "spare_parts_table":
            return ChunkType.SPARE_PARTS_TABLE
        if table_category == "maintenance_interval_table":
            return ChunkType.MAINTENANCE_INTERVAL
        if table_category == "troubleshooting_table":
            return ChunkType.TROUBLESHOOTING
        if table_category == "operation_reference_table":
            return ChunkType.OPERATION_INSTRUCTION
        if table_category in {"technical_data_table", "operating_limits_table"}:
            return ChunkType.TECHNICAL_SPECIFICATION
        if table_category == "certification_table":
            return ChunkType.CERTIFICATION_INFO
        return None

    @staticmethod
    def _has_spare_part_header_row(parser_extra: dict) -> bool:
        table_rows = parser_extra.get("table_rows")
        if not table_rows:
            return False

        header_row = table_rows[0]
        spare_part_header_markers = ("part", "spare part", "part number")
        return any(
            any(marker in cell.strip().lower() for marker in spare_part_header_markers)
            for cell in header_row
        )
