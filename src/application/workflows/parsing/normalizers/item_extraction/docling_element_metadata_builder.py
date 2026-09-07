from typing import Any

from src.application.workflows.parsing.normalizers.docling_item_extractor import (
    DoclingItemExtractor,
)
from src.application.workflows.parsing.normalizers.table_rows.docling_table_extractor import (
    DoclingTableExtractor,
)
from src.application.workflows.parsing.normalizers.docling_value_accessors import (
    clean_text,
    get_value,
)
from src.application.workflows.parsing.normalizers.table_layout.table_reconstruction_result import (
    TableReconstructionResult,
)
from src.application.workflows.parsing.parsing_value_coercion import (
    coerce_positive_int,
)
from src.domain.common import ElementType


class DoclingElementMetadataBuilder:
    def __init__(
        self,
        *,
        item_extractor: DoclingItemExtractor,
        table_extractor: DoclingTableExtractor,
    ) -> None:
        self.item_extractor = item_extractor
        self.table_extractor = table_extractor

    def build(
        self,
        item: Any,
        *,
        raw_ref: str | None,
        element_type: ElementType,
        caption: str | None,
        layout_metadata: dict[str, Any] | None,
        markdown: str | None,
        table_structure: TableReconstructionResult | None,
    ) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "raw_source_type": item.__class__.__name__,
        }
        if layout_metadata:
            metadata.update(layout_metadata)
        label = self.item_extractor.lower_label(item)
        if label:
            metadata["item_label"] = label

        if raw_ref:
            metadata["raw_ref"] = raw_ref

        content_layer = self.item_extractor.extract_content_layer(item)
        if content_layer:
            metadata["content_layer"] = content_layer

        parent_ref = self.item_extractor.extract_parent_ref(item)
        if parent_ref:
            metadata["parent_ref"] = parent_ref

        heading_level = coerce_positive_int(get_value(item, "level"))
        if heading_level is not None:
            metadata["heading_level"] = heading_level

        if element_type == ElementType.TABLE:
            self._apply_table_metadata(
                metadata,
                item=item,
                markdown=markdown,
                table_structure=table_structure,
            )

        if element_type == ElementType.FORM:
            self._apply_form_metadata(metadata, item=item)

        if caption:
            metadata["caption"] = caption

        image_path = get_value(item, "image_path")
        if image_path:
            metadata["image_path"] = image_path

        ocr_text = clean_text(get_value(item, "ocr_text"))
        if ocr_text:
            metadata["ocr_text"] = ocr_text

        ocr_provider = clean_text(get_value(item, "ocr_provider"))
        if ocr_provider:
            metadata["ocr_provider"] = ocr_provider

        ocr_confidence = get_value(item, "ocr_confidence")
        if isinstance(ocr_confidence, (int, float)):
            metadata["ocr_confidence"] = float(ocr_confidence)

        return metadata

    def _apply_table_metadata(
        self,
        metadata: dict[str, Any],
        *,
        item: Any,
        markdown: str | None,
        table_structure: TableReconstructionResult | None,
    ) -> None:
        if markdown:
            metadata["markdown"] = markdown

        rows = table_structure.rows if table_structure is not None else []
        if rows:
            metadata["table_rows"] = rows
            metadata["table_structure_tier"] = "row_grid"

        cell_spans = (
            [span.to_dict() for span in table_structure.cell_spans]
            if table_structure is not None
            else []
        )
        if cell_spans:
            metadata["table_cell_spans"] = cell_spans
            metadata["table_structure_tier"] = "span_aware"

        if table_structure is not None and table_structure.parallel_stream_rows:
            metadata["table_parallel_stream_rows"] = [
                [list(row) for row in stream_rows]
                for stream_rows in table_structure.parallel_stream_rows
            ]
            metadata["table_parallel_stream_count"] = (
                table_structure.parallel_stream_count
            )
            metadata["table_region_partition_version"] = (
                table_structure.reconstruction_version or "1"
            )
            if table_structure.local_reading_order:
                metadata["table_local_reading_order"] = (
                    table_structure.local_reading_order
                )
            metadata["table_structure_tier"] = "parallel_streams"
        if table_structure is not None and table_structure.parallel_stream_descriptors:
            metadata["table_parallel_stream_descriptors"] = [
                descriptor.to_dict()
                for descriptor in table_structure.parallel_stream_descriptors
            ]

        row_count, column_count = self.table_extractor.extract_dimensions(item)
        if rows:
            # `rows` reflects the post-repair grid (DoclingTableRowRepairer's
            # TOC/single-column reconstructors can split or add rows), while
            # extract_dimensions() measures the pre-repair Docling cell grid -
            # trust the actual final rows over the earlier raw dimensions.
            row_count = len(rows)
            column_count = max(len(row) for row in rows)
        if row_count is not None:
            metadata["row_count"] = row_count
        if column_count is not None:
            metadata["column_count"] = column_count

        if markdown and "table_structure_tier" not in metadata:
            metadata["table_structure_tier"] = "markdown_only"

    def _apply_form_metadata(self, metadata: dict[str, Any], *, item: Any) -> None:
        graph = get_value(item, "graph")
        if graph is None:
            return

        cells = list(get_value(graph, "cells") or [])
        links = list(get_value(graph, "links") or [])

        cell_by_id: dict[Any, Any] = {}
        for cell in cells:
            cell_id = get_value(cell, "cell_id")
            if cell_id is not None:
                cell_by_id[cell_id] = cell

        value_cell_id_by_key_id: dict[Any, Any] = {}
        for link in links:
            if self._label_value(get_value(link, "label")) != "to_value":
                continue
            source_id = get_value(link, "source_cell_id")
            target_id = get_value(link, "target_cell_id")
            if source_id is not None and target_id is not None:
                value_cell_id_by_key_id[source_id] = target_id

        fields: list[dict[str, Any]] = []
        for cell in cells:
            label = self._label_value(get_value(cell, "label"))
            if label not in ("key", "checkbox"):
                continue

            cell_id = get_value(cell, "cell_id")
            key_text = clean_text(get_value(cell, "text"))

            value_text = None
            value_cell_id = value_cell_id_by_key_id.get(cell_id)
            if value_cell_id is not None:
                value_cell = cell_by_id.get(value_cell_id)
                if value_cell is not None:
                    value_text = clean_text(get_value(value_cell, "text"))

            if not key_text and not value_text:
                continue

            fields.append(
                {
                    "label": label,
                    "key_text": key_text,
                    "value_text": value_text,
                    "cell_id": cell_id,
                }
            )

        if fields:
            metadata["form_fields"] = fields

    @staticmethod
    def _label_value(value: Any) -> str | None:
        if value is None:
            return None
        # Docling's real GraphLink.label/GraphCell.label are Enum members
        # (GraphLinkLabel is a plain Enum, not a StrEnum -- str() on it gives
        # "GraphLinkLabel.TO_VALUE", not "to_value"), so .value must be read
        # explicitly rather than relying on str(); plain strings (e.g. from
        # dict-shaped test fixtures) have no .value and fall through as-is.
        if hasattr(value, "value"):
            value = value.value
        return str(value).strip().lower() or None
