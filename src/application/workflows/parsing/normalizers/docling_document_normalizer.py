from typing import Any

from src.application.workflows.parsing.normalizers.docling_caption_extractor import (
    DoclingCaptionExtractor,
)
from src.application.workflows.parsing.normalizers.docling_item_extractor import (
    DoclingItemExtractor,
)
from src.application.workflows.parsing.normalizers.docling_layout_metadata_builder import (
    DoclingLayoutMetadataBuilder,
)
from src.application.workflows.parsing.normalizers.docling_provenance_extractor import (
    DoclingProvenanceExtractor,
)
from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)
from src.application.workflows.parsing.normalizers.docling_table_extractor import (
    DoclingTableExtractor,
)
from src.application.workflows.parsing.normalizers.table_layout.table_reconstruction_result import (
    TableReconstructionResult,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.application.workflows.parsing.parsing_value_coercion import (
    coerce_positive_int,
)
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.domain.common import ElementType
from src.shared.exceptions import DocumentNormalizationError


class DoclingDocumentNormalizer:
    def __init__(self) -> None:
        self.layout_metadata_builder = DoclingLayoutMetadataBuilder()
        self.table_extractor = DoclingTableExtractor()
        self.item_extractor = DoclingItemExtractor(self.table_extractor)
        self.provenance_extractor = DoclingProvenanceExtractor()

    def normalize(
        self,
        raw_parsed_document: RawParsedDocument,
        document_id: str,
    ) -> list[CanonicalElement]:
        try:
            raw_document = raw_parsed_document.raw_document
            items = list(self.item_extractor.iter_items(raw_document))
            normalized: list[CanonicalElement] = []
            caption_extractor = DoclingCaptionExtractor(
                raw_document,
                items=items,
            )
            layout_metadata_by_element_ref = self.layout_metadata_builder.build(
                raw_document=raw_document,
                items=items,
                item_extractor=self.item_extractor,
                provenance_extractor=self.provenance_extractor,
            )

            for index, item in enumerate(
                items,
                start=1,
            ):
                if self.item_extractor.should_skip(item):
                    continue

                element_type = self.item_extractor.extract_element_type(item)
                table_markdown = self._extract_table_markdown(
                    item,
                    element_type,
                    raw_document=raw_document,
                )
                table_structure = self._extract_table_structure(item, element_type)
                caption = self._extract_caption_text(
                    item,
                    caption_extractor,
                )
                text = self._extract_text(
                    item,
                    element_type,
                    caption=caption,
                    table_markdown=table_markdown,
                )
                page_start, page_end = self.provenance_extractor.extract_pages(item)
                bbox = self.provenance_extractor.extract_bbox(item)
                section_path = self.item_extractor.extract_section_path(item)
                section_title = self._extract_section_title(element_type, text)
                raw_ref = self.item_extractor.extract_raw_ref(item)
                metadata = self._build_metadata(
                    item,
                    raw_ref=raw_ref,
                    element_type=element_type,
                    caption=caption,
                    layout_metadata=layout_metadata_by_element_ref.get(
                        raw_ref or f"canon_{index}"
                    ),
                    markdown=table_markdown,
                    table_structure=table_structure,
                )

                normalized.append(
                    CanonicalElement(
                        element_id=raw_ref or f"canon_{index}",
                        document_id=document_id,
                        element_type=element_type,
                        text=text,
                        page_start=page_start,
                        page_end=page_end,
                        bbox=bbox,
                        order_index=index,
                        section_title=section_title,
                        section_path=section_path,
                        raw_ref=raw_ref,
                        metadata=metadata,
                    )
                )

            return normalized
        except DocumentNormalizationError:
            raise
        except Exception as exc:
            raise DocumentNormalizationError(
                "Failed to normalize Docling document.",
                details={
                    "file_path": raw_parsed_document.file_path,
                    "parser_name": raw_parsed_document.parser_name,
                },
            ) from exc

    def _extract_text(
        self,
        item: Any,
        element_type: ElementType,
        *,
        caption: str | None,
        table_markdown: str | None,
    ) -> str | None:
        if element_type == ElementType.TABLE:
            return table_markdown

        if element_type == ElementType.PICTURE:
            return self._clean_text(
                caption
                or self._get_value(item, "ocr_text")
                or self._get_value(item, "text")
            )

        for attribute_name in ("text", "orig", "caption", "name"):
            cleaned = self._clean_text(self._get_value(item, attribute_name))
            if cleaned:
                return cleaned

        for method_name in ("export_to_markdown", "to_markdown"):
            method = getattr(item, method_name, None)
            if callable(method):
                try:
                    cleaned = self._clean_text(method())
                except Exception:
                    cleaned = None
                if cleaned:
                    return cleaned

        return None

    def _extract_table_markdown(
        self,
        item: Any,
        element_type: ElementType,
        *,
        raw_document: Any,
    ) -> str | None:
        if element_type != ElementType.TABLE:
            return None

        return self.table_extractor.extract_markdown(
            item,
            doc=raw_document,
        )

    def _extract_caption_text(
        self,
        item: Any,
        caption_extractor: DoclingCaptionExtractor,
    ) -> str | None:
        return self._clean_text(
            caption_extractor.extract_caption(item)
            or self._get_value(item, "caption")
        )

    def _extract_table_structure(
        self,
        item: Any,
        element_type: ElementType,
    ) -> TableReconstructionResult | None:
        if element_type != ElementType.TABLE:
            return None
        return self.table_extractor.extract_structure(item)

    @staticmethod
    def _extract_section_title(
        element_type: ElementType,
        text: str | None,
    ) -> str | None:
        if element_type == ElementType.SECTION_HEADER:
            return text

        return None

    def _build_metadata(
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

        heading_level = coerce_positive_int(self._get_value(item, "level"))
        if heading_level is not None:
            metadata["heading_level"] = heading_level

        if element_type == ElementType.TABLE:
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

        if caption:
            metadata["caption"] = caption

        image_path = self._get_value(item, "image_path")
        if image_path:
            metadata["image_path"] = image_path

        ocr_text = self._clean_text(self._get_value(item, "ocr_text"))
        if ocr_text:
            metadata["ocr_text"] = ocr_text

        ocr_provider = self._clean_text(self._get_value(item, "ocr_provider"))
        if ocr_provider:
            metadata["ocr_provider"] = ocr_provider

        ocr_confidence = self._get_value(item, "ocr_confidence")
        if isinstance(ocr_confidence, (int, float)):
            metadata["ocr_confidence"] = float(ocr_confidence)

        return metadata

    @staticmethod
    def _clean_text(value: Any) -> str | None:
        if value is None:
            return None

        text = repair_docling_text(str(value)).strip()
        return text or None

    @staticmethod
    def _get_value(value: Any, name: str) -> Any:
        if value is None:
            return None

        if isinstance(value, dict):
            return value.get(name)

        return getattr(value, name, None)
