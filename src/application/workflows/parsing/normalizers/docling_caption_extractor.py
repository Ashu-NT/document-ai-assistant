from collections.abc import Iterable
from typing import Any


class DoclingCaptionExtractor:
    def __init__(self, raw_document: Any) -> None:
        self.reference_lookup = self._build_reference_lookup(raw_document)

    def extract_caption(self, item: Any) -> str | None:
        parts: list[str] = []

        for caption_ref in self._iter_values(self._get_value(item, "captions")):
            resolved = self._resolve_reference(caption_ref)
            if resolved is None:
                continue

            text = self._extract_text(resolved)
            if text:
                parts.append(text)

        for child_ref in self._iter_values(self._get_value(item, "children")):
            resolved = self._resolve_reference(child_ref)
            if resolved is None:
                continue

            if self._lower_label(resolved) != "caption":
                continue

            text = self._extract_text(resolved)
            if text:
                parts.append(text)

        unique_parts = list(dict.fromkeys(parts))
        if not unique_parts:
            return None

        return "\n".join(unique_parts)

    def _build_reference_lookup(self, raw_document: Any) -> dict[str, Any]:
        lookup: dict[str, Any] = {}

        for attribute_name in ("texts", "tables", "pictures", "items"):
            for item in list(self._get_value(raw_document, attribute_name) or []):
                raw_ref = self._extract_raw_ref(item)
                if raw_ref:
                    lookup[raw_ref] = item

        iterate_items = getattr(raw_document, "iterate_items", None)
        if callable(iterate_items):
            try:
                iterator = iterate_items(traverse_pictures=True)
            except TypeError:
                try:
                    iterator = iterate_items(with_groups=False, traverse_pictures=True)
                except TypeError:
                    iterator = iterate_items()

            for entry in iterator:
                item = entry[0] if isinstance(entry, tuple) else entry
                raw_ref = self._extract_raw_ref(item)
                if raw_ref and raw_ref not in lookup:
                    lookup[raw_ref] = item

        return lookup

    def _resolve_reference(self, reference: Any) -> Any | None:
        if reference is None:
            return None

        raw_ref = self._extract_reference_value(reference)
        if raw_ref and raw_ref in self.reference_lookup:
            return self.reference_lookup[raw_ref]

        return reference if self._extract_raw_ref(reference) else None

    @staticmethod
    def _extract_text(item: Any) -> str | None:
        for attribute_name in ("text", "orig", "caption", "name"):
            value = DoclingCaptionExtractor._get_value(item, attribute_name)
            if value is None:
                continue

            text = str(value).strip()
            if text:
                return text

        return None

    @staticmethod
    def _extract_reference_value(reference: Any) -> str | None:
        for attribute_name in ("$ref", "ref", "cref", "self_ref"):
            value = DoclingCaptionExtractor._get_value(reference, attribute_name)
            if value is None:
                continue

            text = str(value).strip()
            if text:
                return text

        return None

    @staticmethod
    def _extract_raw_ref(item: Any) -> str | None:
        for attribute_name in ("self_ref", "ref", "id", "uuid"):
            value = DoclingCaptionExtractor._get_value(item, attribute_name)
            if value is None:
                continue

            text = str(value).strip()
            if text:
                return text

        return None

    @staticmethod
    def _lower_label(item: Any) -> str:
        label = DoclingCaptionExtractor._get_value(item, "label")
        if label is None:
            return ""

        value = DoclingCaptionExtractor._get_value(label, "value")
        if value is not None:
            return str(value).lower()

        return str(label).lower()

    @staticmethod
    def _iter_values(value: Any) -> Iterable[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    @staticmethod
    def _get_value(value: Any, name: str) -> Any:
        if value is None:
            return None

        if isinstance(value, dict):
            return value.get(name)

        return getattr(value, name, None)
