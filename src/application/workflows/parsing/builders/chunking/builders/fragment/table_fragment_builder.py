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

    def table_chunk_type(
        self,
        element: CanonicalElement,
        text: str | None,
    ) -> ChunkType:
        parser_extra = resolve_parser_extra(element)
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
