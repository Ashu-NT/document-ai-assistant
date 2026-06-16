from src.domain.common import BoundingBox, SourceLocation


def bbox_to_columns(source: SourceLocation) -> dict[str, float | int | None]:
    bbox = source.bbox

    return {
        "page_start": source.page_start,
        "page_end": source.page_end,
        "bbox_x1": bbox.x1 if bbox else None,
        "bbox_y1": bbox.y1 if bbox else None,
        "bbox_x2": bbox.x2 if bbox else None,
        "bbox_y2": bbox.y2 if bbox else None,
    }


def columns_to_source_location(
    *,
    page_start: int | None,
    page_end: int | None,
    bbox_x1: float | None = None,
    bbox_y1: float | None = None,
    bbox_x2: float | None = None,
    bbox_y2: float | None = None,
) -> SourceLocation:
    bbox = None

    if all(value is not None for value in [bbox_x1, bbox_y1, bbox_x2, bbox_y2]):
        bbox = BoundingBox(
            x1=bbox_x1,
            y1=bbox_y1,
            x2=bbox_x2,
            y2=bbox_y2,
        )

    return SourceLocation(
        page_start=page_start,
        page_end=page_end,
        bbox=bbox,
    )