from typing import Any

from src.domain.common import BoundingBox


class DoclingProvenanceExtractor:
    def extract_pages(self, item: Any) -> tuple[int | None, int | None]:
        provenances = self.extract_provenances(item)
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

    def extract_bbox(self, item: Any) -> BoundingBox | None:
        provenances = self.extract_provenances(item)
        for provenance in provenances:
            bbox = self._bbox_from_object(self._get_value(provenance, "bbox"))
            if bbox is not None:
                return bbox

        return self._bbox_from_object(self._get_value(item, "bbox"))

    def extract_provenances(self, item: Any) -> list[Any]:
        for attribute_name in ("prov", "provenance", "provenances"):
            value = self._get_value(item, attribute_name)
            if value is None:
                continue

            if isinstance(value, list):
                return value

            return [value]

        return []

    @classmethod
    def _page_number_from_provenance(cls, provenance: Any) -> int | None:
        for attribute_name in ("page_no", "page", "page_index"):
            value = cls._get_value(provenance, attribute_name)
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

    @classmethod
    def _bbox_from_object(cls, raw_bbox: Any) -> BoundingBox | None:
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
                cls._get_value(raw_bbox, attribute_name)
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
    def _get_value(value: Any, name: str) -> Any:
        if value is None:
            return None

        if isinstance(value, dict):
            return value.get(name)

        return getattr(value, name, None)
