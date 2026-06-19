from collections.abc import Iterable
from typing import Any

from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.domain.common import BoundingBox, ElementType
from src.shared.exceptions import DocumentNormalizationError


class DoclingDocumentNormalizer:
    def normalize(
        self,
        raw_parsed_document: RawParsedDocument,
        document_id: str,
    ) -> list[CanonicalElement]:
        try:
            normalized: list[CanonicalElement] = []

            for index, item in enumerate(
                self._iter_items(raw_parsed_document.raw_document),
                start=1,
            ):
                element_type = self._extract_element_type(item)
                text = self._extract_text(item)
                page_start, page_end = self._extract_pages(item)
                bbox = self._extract_bbox(item)
                section_path = self._extract_section_path(item)
                section_title = self._extract_section_title(item, text, section_path)
                raw_ref = self._extract_raw_ref(item)
                metadata = self._build_metadata(item)

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

    def _iter_items(self, raw_document: Any) -> Iterable[Any]:
        if hasattr(raw_document, "iterate_items"):
            yield from self._iter_from_iterate_items(raw_document)
            return

        yielded = False
        for attribute_name in ("texts", "tables", "pictures", "items"):
            for item in list(getattr(raw_document, attribute_name, []) or []):
                yielded = True
                yield item

        if yielded:
            return

        body = getattr(raw_document, "body", None)
        children = getattr(body, "children", None)
        if children:
            yield from self._iter_children(children)

    def _iter_from_iterate_items(self, raw_document: Any) -> Iterable[Any]:
        try:
            iterator = raw_document.iterate_items(
                with_groups=True,
                traverse_pictures=True,
            )
        except TypeError:
            iterator = raw_document.iterate_items()

        for entry in iterator:
            if isinstance(entry, tuple):
                yield entry[0]
            else:
                yield entry

    def _iter_children(self, children: Any) -> Iterable[Any]:
        for child in list(children or []):
            yield child
            nested_children = getattr(child, "children", None)
            if nested_children:
                yield from self._iter_children(nested_children)

    def _extract_element_type(self, item: Any) -> ElementType:
        label = self._lower_label(item)
        class_name = item.__class__.__name__.lower()
        value = label or class_name

        if "section_header" in value:
            return ElementType.SECTION_HEADER
        if "title" in value:
            return ElementType.TITLE
        if "table" in value:
            return ElementType.TABLE
        if "picture" in value or "image" in value or "figure" in value:
            return ElementType.PICTURE
        if "list_item" in value:
            return ElementType.LIST_ITEM
        if "formula" in value:
            return ElementType.FORMULA
        if "code" in value:
            return ElementType.CODE
        if "key_value" in value:
            return ElementType.KEY_VALUE
        if "form" in value:
            return ElementType.FORM
        if "caption" in value:
            return ElementType.CAPTION
        if "text" in value or "paragraph" in value:
            return ElementType.TEXT

        return ElementType.TEXT

    def _extract_text(self, item: Any) -> str | None:
        label = self._lower_label(item)
        metadata = self._build_metadata(item)

        if "markdown" in metadata:
            return self._clean_text(metadata["markdown"])

        if label == "picture":
            return self._clean_text(
                metadata.get("caption")
                or metadata.get("ocr_text")
                or getattr(item, "text", None)
            )

        for attribute_name in ("text", "orig", "caption", "name"):
            value = getattr(item, attribute_name, None)
            cleaned = self._clean_text(value)
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

    def _extract_pages(self, item: Any) -> tuple[int | None, int | None]:
        provenances = self._extract_provenances(item)
        if not provenances:
            return (None, None)

        page_numbers = [
            page_no
            for provenance in provenances
            if (page_no := self._page_number_from_provenance(provenance)) is not None
        ]
        if not page_numbers:
            return (None, None)

        return (page_numbers[0], page_numbers[-1])

    def _extract_bbox(self, item: Any) -> BoundingBox | None:
        provenances = self._extract_provenances(item)
        for provenance in provenances:
            bbox = self._bbox_from_object(getattr(provenance, "bbox", None))
            if bbox is not None:
                return bbox

        return self._bbox_from_object(getattr(item, "bbox", None))

    def _extract_section_title(
        self,
        item: Any,
        text: str | None,
        section_path: list[str],
    ) -> str | None:
        for attribute_name in ("section_title", "title", "header_text"):
            value = getattr(item, attribute_name, None)
            cleaned = self._clean_text(value)
            if cleaned:
                return cleaned

        if section_path:
            return section_path[-1]

        return text

    def _extract_section_path(self, item: Any) -> list[str]:
        for attribute_name in ("section_path", "path", "section_titles", "headings"):
            value = getattr(item, attribute_name, None)
            parsed = self._coerce_section_path(value)
            if parsed:
                return parsed

        return []

    def _extract_raw_ref(self, item: Any) -> str | None:
        for attribute_name in ("self_ref", "ref", "id", "uuid"):
            value = getattr(item, attribute_name, None)
            if value is None:
                continue

            text = str(value).strip()
            if text:
                return text

        return None

    def _build_metadata(self, item: Any) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "raw_source_type": item.__class__.__name__,
        }
        label = self._lower_label(item)
        if label:
            metadata["item_label"] = label

        markdown = self._extract_markdown(item)
        if markdown:
            metadata["markdown"] = markdown

        caption = self._clean_text(getattr(item, "caption", None))
        if caption:
            metadata["caption"] = caption

        image_path = getattr(item, "image_path", None)
        if image_path:
            metadata["image_path"] = image_path

        ocr_text = self._clean_text(getattr(item, "ocr_text", None))
        if ocr_text:
            metadata["ocr_text"] = ocr_text

        return metadata

    def _extract_markdown(self, item: Any) -> str | None:
        for attribute_name in ("markdown", "md"):
            value = getattr(item, attribute_name, None)
            cleaned = self._clean_text(value)
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
    def _clean_text(value: Any) -> str | None:
        if value is None:
            return None

        text = str(value).strip()
        return text or None

    @staticmethod
    def _lower_label(item: Any) -> str:
        label = getattr(item, "label", None)
        if label is None:
            return ""

        if hasattr(label, "value"):
            return str(label.value).lower()

        return str(label).lower()

    @staticmethod
    def _extract_provenances(item: Any) -> list[Any]:
        for attribute_name in ("prov", "provenance", "provenances"):
            value = getattr(item, attribute_name, None)
            if value is None:
                continue

            if isinstance(value, list):
                return value

            return [value]

        return []

    @staticmethod
    def _page_number_from_provenance(provenance: Any) -> int | None:
        for attribute_name in ("page_no", "page", "page_index"):
            value = getattr(provenance, attribute_name, None)
            if value is None:
                continue

            try:
                page_no = int(value)
            except (TypeError, ValueError):
                return None

            if attribute_name == "page_index":
                return page_no + 1

            return page_no

        return None

    @staticmethod
    def _bbox_from_object(raw_bbox: Any) -> BoundingBox | None:
        if raw_bbox is None:
            return None

        attribute_sets = [
            ("x1", "y1", "x2", "y2"),
            ("x0", "y0", "x1", "y1"),
            ("l", "t", "r", "b"),
            ("left", "top", "right", "bottom"),
        ]

        for attribute_names in attribute_sets:
            values = [
                getattr(raw_bbox, attribute_name, None)
                for attribute_name in attribute_names
            ]
            if any(value is None for value in values):
                continue

            return BoundingBox(
                x1=float(values[0]),
                y1=float(values[1]),
                x2=float(values[2]),
                y2=float(values[3]),
            )

        return None

    @staticmethod
    def _coerce_section_path(value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, list):
            return [str(part).strip() for part in value if str(part).strip()]

        if isinstance(value, tuple):
            return [str(part).strip() for part in value if str(part).strip()]

        text = str(value).strip()
        if not text:
            return []

        if ">" in text:
            return [
                part.strip()
                for part in text.split(">")
                if part.strip()
            ]

        return [text]
