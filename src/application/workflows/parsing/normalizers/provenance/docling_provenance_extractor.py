from typing import Any

from src.application.workflows.parsing.normalizers.docling_bbox_normalizer import (
    DoclingBBoxNormalizer,
)
from src.application.workflows.parsing.normalizers.docling_page_height_resolver import (
    DoclingPageHeightResolver,
)
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

    def extract_bbox(
        self,
        item: Any,
        *,
        raw_document: Any | None = None,
        default_page_number: int | None = None,
    ) -> BoundingBox | None:
        provenances = self.extract_provenances(item)
        for provenance in provenances:
            bbox = self._bbox_from_object(
                self._get_value(provenance, "bbox"),
                page_height=DoclingPageHeightResolver.resolve(
                    raw_document,
                    self._page_number_from_provenance(provenance)
                    or default_page_number,
                ),
            )
            if bbox is not None:
                return bbox

        return self._bbox_from_object(
            self._get_value(item, "bbox"),
            page_height=DoclingPageHeightResolver.resolve(
                raw_document,
                self._page_number_from_provenance(item) or default_page_number,
            ),
        )

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

    @staticmethod
    def _bbox_from_object(
        raw_bbox: Any,
        *,
        page_height: float | None = None,
    ) -> BoundingBox | None:
        return DoclingBBoxNormalizer.normalize(raw_bbox, page_height=page_height)

    @staticmethod
    def _get_value(value: Any, name: str) -> Any:
        if value is None:
            return None

        if isinstance(value, dict):
            return value.get(name)

        return getattr(value, name, None)
