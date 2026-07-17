from __future__ import annotations

from src.application.workflows.parsing.tables.rendering.structured_row_renderer import (
    StructuredRowRenderer,
)
from src.application.workflows.parsing.tables.structure.table_shape_resolver import (
    TableShapeResolver,
)
from src.domain.assets import TableAsset


class TableAssetStructuredTextRenderer:
    def __init__(
        self,
        structured_row_renderer: StructuredRowRenderer | None = None,
        table_shape_resolver: TableShapeResolver | None = None,
    ) -> None:
        self.structured_row_renderer = structured_row_renderer or StructuredRowRenderer()
        self.table_shape_resolver = table_shape_resolver or TableShapeResolver()

    def render(self, table: TableAsset) -> str | None:
        table_shape = self.table_shape_resolver.resolve(table)
        if table.parallel_stream_rows:
            stream_renderings: list[str] = []
            for index, rows in enumerate(table.parallel_stream_rows, start=1):
                rendered = self.structured_row_renderer.render(
                    rows,
                    table_category=table.table_category,
                    table_shape=table_shape,
                )
                if not rendered:
                    continue
                if len(table.parallel_stream_rows) > 1:
                    stream_renderings.append(
                        f"Parallel Table Stream {index}:\n{rendered}"
                    )
                else:
                    stream_renderings.append(rendered)
            if stream_renderings:
                return "\n\n".join(stream_renderings)
        return self.structured_row_renderer.render(
            table.rows,
            table_category=table.table_category,
            table_shape=table_shape,
        )
