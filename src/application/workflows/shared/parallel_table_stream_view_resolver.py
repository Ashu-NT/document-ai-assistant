from __future__ import annotations

from dataclasses import dataclass

from src.application.workflows.shared.parallel_table_stream_label_builder import (
    ParallelTableStreamLabelBuilder,
)
from src.domain.assets import TableAsset, TableParallelStream


@dataclass(frozen=True, slots=True)
class ParallelTableStreamView:
    stream_index: int
    stream_count: int
    title: str
    short_label: str
    rows: tuple[tuple[str, ...], ...]
    descriptor: TableParallelStream | None = None


class ParallelTableStreamViewResolver:
    def __init__(
        self,
        label_builder: ParallelTableStreamLabelBuilder | None = None,
    ) -> None:
        self.label_builder = label_builder or ParallelTableStreamLabelBuilder()

    def build(self, table: TableAsset) -> list[ParallelTableStreamView]:
        if not table.parallel_stream_rows:
            return []
        stream_count = len(table.parallel_stream_rows)
        views: list[ParallelTableStreamView] = []
        for stream_index, rows in enumerate(table.parallel_stream_rows, start=1):
            descriptor = self._descriptor_for(table, stream_index)
            views.append(
                ParallelTableStreamView(
                    stream_index=stream_index,
                    stream_count=stream_count,
                    title=self.label_builder.build_title(
                        stream_index=stream_index,
                        stream_count=stream_count,
                        descriptor=descriptor,
                    ),
                    short_label=self.label_builder.build_short_label(
                        stream_index=stream_index,
                        stream_count=stream_count,
                        descriptor=descriptor,
                    ),
                    rows=tuple(tuple(str(cell) for cell in row) for row in rows),
                    descriptor=descriptor,
                )
            )
        return views

    @staticmethod
    def _descriptor_for(
        table: TableAsset,
        stream_index: int,
    ) -> TableParallelStream | None:
        if len(table.parallel_stream_descriptors) < stream_index:
            return None
        return table.parallel_stream_descriptors[stream_index - 1]
