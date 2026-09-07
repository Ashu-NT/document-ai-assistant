from typing import Any

from src.domain.common import BoundingBox


class DoclingBBoxNormalizer:
    """Converts Docling geometry to the pipeline's BOTTOMLEFT convention."""

    CANONICAL_ORIGIN = "BOTTOMLEFT"
    _TOPLEFT = "TOPLEFT"
    _BOTTOMLEFT = "BOTTOMLEFT"
    _ATTRIBUTE_SETS = (
        ("x1", "y1", "x2", "y2"),
        ("x0", "y0", "x1", "y1"),
        ("l", "t", "r", "b"),
        ("left", "top", "right", "bottom"),
    )

    @classmethod
    def normalize(
        cls,
        raw_bbox: Any,
        *,
        page_height: float | None,
    ) -> BoundingBox | None:
        coordinates = cls._extract_coordinates(raw_bbox)
        if coordinates is None:
            return None
        left, first_y, right, second_y = coordinates
        origin = cls._extract_origin(raw_bbox)

        if origin == cls._TOPLEFT:
            if page_height is None or page_height <= 0:
                return None
            top = page_height - min(first_y, second_y)
            bottom = page_height - max(first_y, second_y)
        elif origin == cls._BOTTOMLEFT:
            top = max(first_y, second_y)
            bottom = min(first_y, second_y)
        else:
            # Origin-less inputs predate origin preservation and already use
            # the canonical top-then-bottom ordering in this application.
            top = first_y
            bottom = second_y

        return BoundingBox(
            x1=min(left, right),
            y1=top,
            x2=max(left, right),
            y2=bottom,
        )

    @classmethod
    def _extract_coordinates(
        cls,
        raw_bbox: Any,
    ) -> tuple[float, float, float, float] | None:
        if raw_bbox is None:
            return None
        for attribute_names in cls._ATTRIBUTE_SETS:
            values = [cls._get_value(raw_bbox, name) for name in attribute_names]
            if any(value is None for value in values):
                continue
            try:
                converted = [float(value) for value in values]
            except (TypeError, ValueError):
                return None
            return converted[0], converted[1], converted[2], converted[3]
        return None

    @classmethod
    def _extract_origin(cls, raw_bbox: Any) -> str | None:
        raw_origin = cls._get_value(raw_bbox, "coord_origin")
        if raw_origin is None:
            return None
        value = cls._get_value(raw_origin, "value") or raw_origin
        normalized = str(value).rsplit(".", 1)[-1].strip().upper()
        return normalized if normalized in {cls._TOPLEFT, cls._BOTTOMLEFT} else None

    @staticmethod
    def _get_value(value: Any, name: str) -> Any:
        if isinstance(value, dict):
            return value.get(name)
        return getattr(value, name, None)
