from __future__ import annotations

from src.domain.assets import TableCellSpan, TableParallelStream
from src.domain.common import BoundingBox


class ParallelTableStreamDescriptorBuilder:
    def build(
        self,
        groups: list[tuple[float, list[TableCellSpan], list[list[str]], float]],
    ) -> list[TableParallelStream]:
        descriptors: list[TableParallelStream] = []
        for stream_index, (_, spans, rows, _) in enumerate(groups, start=1):
            descriptors.append(
                TableParallelStream(
                    stream_index=stream_index,
                    source_row_start=min((span.row_start for span in spans), default=0),
                    source_row_end=max((span.row_end for span in spans), default=0),
                    source_col_start=min((span.col_start for span in spans), default=0),
                    source_col_end=max((span.col_end for span in spans), default=0),
                    row_count=len(rows),
                    column_count=max((len(row) for row in rows), default=0),
                    page_number=next(
                        (span.page_number for span in spans if span.page_number is not None),
                        None,
                    ),
                    center_x=self._mean_center_x(spans),
                    bbox=self._merge_bbox(spans),
                )
            )
        return descriptors

    @staticmethod
    def _mean_center_x(spans: list[TableCellSpan]) -> float | None:
        centers = [
            (span.bbox.x1 + span.bbox.x2) / 2.0
            for span in spans
            if span.bbox is not None
        ]
        if not centers:
            return None
        return sum(centers) / len(centers)

    @staticmethod
    def _merge_bbox(spans: list[TableCellSpan]) -> BoundingBox | None:
        bboxes = [span.bbox for span in spans if span.bbox is not None]
        if not bboxes:
            return None
        return BoundingBox(
            x1=min(bbox.x1 for bbox in bboxes),
            y1=min(bbox.y1 for bbox in bboxes),
            x2=max(bbox.x2 for bbox in bboxes),
            y2=max(bbox.y2 for bbox in bboxes),
        )
