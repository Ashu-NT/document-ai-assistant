from collections.abc import Iterable
from typing import Any

from src.application.workflows.parsing.normalizers.docling_table_extractor import (
    DoclingTableExtractor,
)
from src.domain.common import ElementType


class DoclingItemExtractor:
    def __init__(self, table_extractor: DoclingTableExtractor) -> None:
        self.table_extractor = table_extractor

    def iter_items(self, raw_document: Any) -> Iterable[Any]:
        if hasattr(raw_document, "iterate_items"):
            yield from self._iter_from_iterate_items(raw_document)
            return

        yielded = False
        for attribute_name in ("texts", "tables", "pictures", "items"):
            for item in list(self._get_value(raw_document, attribute_name) or []):
                yielded = True
                yield item

        if yielded:
            return

        body = self._get_value(raw_document, "body")
        children = self._get_value(body, "children")
        if children:
            yield from self._iter_children(children)

    def should_skip(self, item: Any) -> bool:
        raw_ref = self.extract_raw_ref(item)
        label = self.lower_label(item)
        content_layer = self.extract_content_layer(item)
        name = self.clean_text(self._get_value(item, "name"))
        text = self.clean_text(self._get_value(item, "text"))

        if raw_ref in {"#/body", "#/furniture"}:
            return True

        if content_layer == "furniture":
            return True

        if label in {"page_header", "page_footer"}:
            return True

        if name == "_root_":
            return True

        if text == "_root_":
            return True

        return False

    def extract_element_type(self, item: Any) -> ElementType:
        if self.table_extractor.is_table_item(item):
            return ElementType.TABLE

        label = self.lower_label(item)
        class_name = item.__class__.__name__.lower()
        value = label or class_name

        if "section_header" in value:
            return ElementType.SECTION_HEADER
        if "title" in value:
            return ElementType.TITLE
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

    def extract_section_path(self, item: Any) -> list[str]:
        for attribute_name in ("section_path", "path", "section_titles", "headings"):
            value = self._get_value(item, attribute_name)
            parsed = self._coerce_section_path(value)
            if parsed:
                return parsed

        return []

    def extract_raw_ref(self, item: Any) -> str | None:
        for attribute_name in ("self_ref", "ref", "id", "uuid"):
            value = self._get_value(item, attribute_name)
            if value is None:
                continue

            text = str(value).strip()
            if text:
                return text

        return None

    def extract_content_layer(self, item: Any) -> str | None:
        value = self._get_value(item, "content_layer")
        if value is None:
            return None

        text = str(value).strip()
        return text or None

    def extract_parent_ref(self, item: Any) -> str | None:
        parent = self._get_value(item, "parent")
        if parent is None:
            return None

        for attribute_name in ("$ref", "ref", "cref", "self_ref"):
            value = self._get_value(parent, attribute_name)
            if value is None:
                continue

            text = str(value).strip()
            if text:
                return text

        return None

    def lower_label(self, item: Any) -> str:
        label = self._get_value(item, "label")
        if label is None:
            return ""

        value = self._get_value(label, "value")
        if value is not None:
            return str(value).lower()

        return str(label).lower()

    @staticmethod
    def clean_text(value: Any) -> str | None:
        if value is None:
            return None

        text = str(value).strip()
        return text or None

    def _iter_from_iterate_items(self, raw_document: Any) -> Iterable[Any]:
        try:
            iterator = raw_document.iterate_items(
                with_groups=False,
                traverse_pictures=True,
            )
        except TypeError:
            try:
                iterator = raw_document.iterate_items(
                    traverse_pictures=True,
                )
            except TypeError:
                iterator = raw_document.iterate_items()

        for entry in iterator:
            yield entry[0] if isinstance(entry, tuple) else entry

    def _iter_children(self, children: Any) -> Iterable[Any]:
        for child in list(children or []):
            yield child
            nested_children = self._get_value(child, "children")
            if nested_children:
                yield from self._iter_children(nested_children)

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
            return [part.strip() for part in text.split(">") if part.strip()]

        return [text]

    @staticmethod
    def _get_value(value: Any, name: str) -> Any:
        if value is None:
            return None

        if isinstance(value, dict):
            return value.get(name)

        return getattr(value, name, None)
