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
from src.application.workflows.shared.table_category import TableCategory
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
            "table_shape": str(parser_extra.get("table_shape") or "").strip() or None,
            "table_structure_quality": coerce_float(
                parser_extra.get("table_structure_quality")
            ),
            "header_paths": TableFragmentBuilder._clean_header_paths(
                parser_extra.get("table_header_paths_json")
            ),
            "axis_summary": TableFragmentBuilder._clean_axis_summary(
                parser_extra.get("table_axis_summary")
            ),
        }

    @staticmethod
    def _clean_header_paths(value: object) -> list[list[str]]:
        if not isinstance(value, list):
            return []
        return [
            [str(part) for part in path if str(part).strip()]
            for path in value
            if isinstance(path, list)
        ]

    @staticmethod
    def _clean_axis_summary(value: object) -> dict[str, str]:
        if not isinstance(value, dict):
            return {}
        return {
            str(key): str(axis_value)
            for key, axis_value in value.items()
            if str(key).strip() and str(axis_value).strip()
        }

    @staticmethod
    def merge_family_table_metadata(
        elements: list[CanonicalElement],
    ) -> dict[str, object]:
        """Reconciles table_shape/table_structure_quality/header_paths/axis_summary
        across every member of a logical table family, mirroring the merge rules
        already used on the QA side (table_evidence_hydrator.py) for consistency."""
        per_element_metadata = [
            TableFragmentBuilder.table_metadata(element) for element in elements
        ]

        table_shape = next(
            (
                metadata["table_shape"]
                for metadata in per_element_metadata
                if metadata["table_shape"]
            ),
            None,
        )
        table_structure_quality = next(
            (
                metadata["table_structure_quality"]
                for metadata in per_element_metadata
                if metadata["table_structure_quality"] is not None
            ),
            None,
        )

        header_paths: list[list[str]] = []
        seen_paths: set[tuple[str, ...]] = set()
        for metadata in per_element_metadata:
            for path in metadata["header_paths"]:
                cleaned = tuple(path)
                if not cleaned or cleaned in seen_paths:
                    continue
                seen_paths.add(cleaned)
                header_paths.append(list(cleaned))

        axis_summary: dict[str, str] = {}
        for metadata in per_element_metadata:
            for key, value in metadata["axis_summary"].items():
                if key not in axis_summary:
                    axis_summary[key] = value

        return {
            "table_shape": table_shape,
            "table_structure_quality": table_structure_quality,
            "header_paths": header_paths,
            "axis_summary": axis_summary,
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
        if table_category == TableCategory.SPARE_PARTS_TABLE:
            return ChunkType.SPARE_PARTS_TABLE
        if table_category == TableCategory.MAINTENANCE_INTERVAL_TABLE:
            return ChunkType.MAINTENANCE_INTERVAL
        if table_category == TableCategory.TROUBLESHOOTING_TABLE:
            return ChunkType.TROUBLESHOOTING
        if table_category == TableCategory.OPERATION_REFERENCE_TABLE:
            return ChunkType.OPERATION_INSTRUCTION
        if table_category in {
            TableCategory.TECHNICAL_DATA_TABLE,
            TableCategory.OPERATING_LIMITS_TABLE,
        }:
            return ChunkType.TECHNICAL_SPECIFICATION
        if table_category == TableCategory.CERTIFICATION_TABLE:
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
