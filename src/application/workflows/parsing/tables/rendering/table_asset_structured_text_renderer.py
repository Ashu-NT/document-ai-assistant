from __future__ import annotations

from src.application.workflows.parsing.tables.rendering.structured_row_renderer import (
    StructuredRowRenderer,
)
from src.application.workflows.parsing.tables.structure.table_shape_resolver import (
    TableShapeResolver,
)
from src.application.workflows.shared.parallel_table_stream_view_resolver import (
    ParallelTableStreamViewResolver,
)
from src.domain.assets import TableAsset


class TableAssetStructuredTextRenderer:
    def __init__(
        self,
        structured_row_renderer: StructuredRowRenderer | None = None,
        table_shape_resolver: TableShapeResolver | None = None,
        stream_view_resolver: ParallelTableStreamViewResolver | None = None,
    ) -> None:
        self.structured_row_renderer = structured_row_renderer or StructuredRowRenderer()
        self.table_shape_resolver = table_shape_resolver or TableShapeResolver()
        self.stream_view_resolver = stream_view_resolver or ParallelTableStreamViewResolver()

    def render(self, table: TableAsset) -> str | None:
        table_shape = self.table_shape_resolver.resolve(table)
        stream_views = self.stream_view_resolver.build(table)
        if stream_views:
            stream_renderings: list[str] = []
            for stream_view in stream_views:
                rendered = self.structured_row_renderer.render(
                    [list(row) for row in stream_view.rows],
                    table_category=table.table_category,
                    table_shape=table_shape,
                )
                if not rendered:
                    continue
                if stream_view.stream_count > 1:
                    stream_renderings.append(f"{stream_view.title}:\n{rendered}")
                else:
                    stream_renderings.append(rendered)
            if stream_renderings:
                return "\n\n".join(stream_renderings)
        return self.structured_row_renderer.render(
            table.rows,
            table_category=table.table_category,
            table_shape=table_shape,
        )
