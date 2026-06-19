from typing import Any

from src.application.workflows.parsing.normalizers.docling_caption_extractor import (
    DoclingCaptionExtractor,
)
from src.application.workflows.parsing.normalizers.docling_item_extractor import (
    DoclingItemExtractor,
)
from src.application.workflows.parsing.normalizers.docling_provenance_extractor import (
    DoclingProvenanceExtractor,
)
from src.application.workflows.parsing.normalizers.docling_table_extractor import (
    DoclingTableExtractor,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.domain.common import ElementType
from src.shared.exceptions import DocumentNormalizationError


class DoclingDocumentNormalizer:
    def __init__(self) -> None:
        self.table_extractor = DoclingTableExtractor()
        self.item_extractor = DoclingItemExtractor(self.table_extractor)
        self.provenance_extractor = DoclingProvenanceExtractor()

    def normalize(
        self,
        raw_parsed_document: RawParsedDocument,
        document_id: str,
    ) -> list[CanonicalElement]:
        try:
            normalized: list[CanonicalElement] = []
            caption_extractor = DoclingCaptionExtractor(raw_parsed_document.raw_document)

            for index, item in enumerate(
                self.item_extractor.iter_items(raw_parsed_document.raw_document),
                start=1,
            ):
                if self.item_extractor.should_skip(item):
                    continue

                element_type = self.item_extractor.extract_element_type(item)
                text = self._extract_text(item, element_type, caption_extractor)
                page_start, page_end = self.provenance_extractor.extract_pages(item)
                bbox = self.provenance_extractor.extract_bbox(item)
                section_path = self.item_extractor.extract_section_path(item)
                section_title = self._extract_section_title(element_type, text)
                raw_ref = self.item_extractor.extract_raw_ref(item)
                metadata = self._build_metadata(
                    item,
                    raw_ref=raw_ref,
                    element_type=element_type,
                    caption_extractor=caption_extractor,
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
        caption_extractor: DoclingCaptionExtractor,
    ) -> str | None:
        if element_type == ElementType.TABLE:
            return self.table_extractor.extract_markdown(item)

        if element_type == ElementType.PICTURE:
            return self._clean_text(
                caption_extractor.extract_caption(item)
                or self._get_value(item, "caption")
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
        caption_extractor: DoclingCaptionExtractor,
    ) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "raw_source_type": item.__class__.__name__,
        }
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

        heading_level = self._coerce_positive_int(self._get_value(item, "level"))
        if heading_level is not None:
            metadata["heading_level"] = heading_level

        if element_type == ElementType.TABLE:
            markdown = self.table_extractor.extract_markdown(item)
            if markdown:
                metadata["markdown"] = markdown

            row_count, column_count = self.table_extractor.extract_dimensions(item)
            if row_count is not None:
                metadata["row_count"] = row_count
            if column_count is not None:
                metadata["column_count"] = column_count

        caption = self._clean_text(
            caption_extractor.extract_caption(item)
            or self._get_value(item, "caption")
        )
        if caption:
            metadata["caption"] = caption

        image_path = self._get_value(item, "image_path")
        if image_path:
            metadata["image_path"] = image_path

        ocr_text = self._clean_text(self._get_value(item, "ocr_text"))
        if ocr_text:
            metadata["ocr_text"] = ocr_text

        return metadata

    @staticmethod
    def _clean_text(value: Any) -> str | None:
        if value is None:
            return None

        text = str(value).strip()
        return text or None

    @staticmethod
    def _coerce_positive_int(value: Any) -> int | None:
        if value is None:
            return None

        try:
            number = int(value)
        except (TypeError, ValueError):
            return None

        return number if number > 0 else None

    @staticmethod
    def _get_value(value: Any, name: str) -> Any:
        if value is None:
            return None

        if isinstance(value, dict):
            return value.get(name)

        return getattr(value, name, None)
