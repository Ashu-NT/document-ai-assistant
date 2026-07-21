from __future__ import annotations

from dataclasses import replace as dataclass_replace

from src.application.workflows.extraction.table_payload.generic_table_payload_builder import (
    GenericTablePayloadBuilder,
)
from src.application.workflows.extraction.table_payload.maintenance_schedule_payload_builder import (
    MaintenanceSchedulePayloadBuilder,
)
from src.application.workflows.extraction.table_payload.performance_curve_payload_builder import (
    PerformanceCurvePayloadBuilder,
)
from src.application.workflows.extraction.table_payload.spare_parts_table_payload_builder import (
    SparePartsTablePayloadBuilder,
)
from src.application.workflows.extraction.table_payload.specification_matrix_payload_builder import (
    SpecificationMatrixPayloadBuilder,
)
from src.application.workflows.extraction.table_payload.troubleshooting_table_payload_builder import (
    TroubleshootingTablePayloadBuilder,
)
from src.application.workflows.shared.parallel_table_stream_view_resolver import (
    ParallelTableStreamViewResolver,
)
from src.domain.assets import TableAsset


class ExtractionTablePayloadRenderer:
    def __init__(
        self,
        *,
        spare_parts_builder: SparePartsTablePayloadBuilder | None = None,
        troubleshooting_builder: TroubleshootingTablePayloadBuilder | None = None,
        maintenance_schedule_builder: (
            MaintenanceSchedulePayloadBuilder | None
        ) = None,
        specification_matrix_builder: (
            SpecificationMatrixPayloadBuilder | None
        ) = None,
        performance_curve_builder: PerformanceCurvePayloadBuilder | None = None,
        generic_builder: GenericTablePayloadBuilder | None = None,
        stream_view_resolver: ParallelTableStreamViewResolver | None = None,
    ) -> None:
        self.spare_parts_builder = spare_parts_builder or SparePartsTablePayloadBuilder()
        self.troubleshooting_builder = (
            troubleshooting_builder or TroubleshootingTablePayloadBuilder()
        )
        self.maintenance_schedule_builder = (
            maintenance_schedule_builder or MaintenanceSchedulePayloadBuilder()
        )
        self.specification_matrix_builder = (
            specification_matrix_builder or SpecificationMatrixPayloadBuilder()
        )
        self.performance_curve_builder = (
            performance_curve_builder or PerformanceCurvePayloadBuilder()
        )
        self.generic_builder = generic_builder or GenericTablePayloadBuilder()
        self.stream_view_resolver = stream_view_resolver or ParallelTableStreamViewResolver()

    def render(self, table: TableAsset, *, chunk_type: str | None = None) -> str | None:
        if table.parallel_stream_rows:
            stream_renderings = self._render_parallel_streams(
                table,
                chunk_type=chunk_type,
            )
            if stream_renderings:
                return stream_renderings
        return self._render_single(table, chunk_type=chunk_type)

    def _render_parallel_streams(
        self,
        table: TableAsset,
        *,
        chunk_type: str | None,
    ) -> str | None:
        rendered_streams: list[str] = []
        for stream_view in self.stream_view_resolver.build(table):
            descriptor = stream_view.descriptor
            stream_table = dataclass_replace(
                table,
                rows=[list(row) for row in stream_view.rows],
                parallel_stream_rows=[],
                parallel_stream_descriptors=[],
                row_count=(
                    descriptor.row_count
                    if descriptor is not None
                    else len(stream_view.rows)
                ),
                column_count=(
                    descriptor.column_count
                    if descriptor is not None
                    else max((len(row) for row in stream_view.rows), default=0)
                ),
            )
            rendered = self._render_single(stream_table, chunk_type=chunk_type)
            if not rendered:
                continue
            if stream_view.stream_count > 1:
                rendered_streams.append(f"{stream_view.title}:\n{rendered}")
            else:
                rendered_streams.append(rendered)
        if not rendered_streams:
            return None
        return "\n\n".join(rendered_streams)

    def _render_single(self, table: TableAsset, *, chunk_type: str | None) -> str | None:
        for builder in (
            self.spare_parts_builder,
            self.troubleshooting_builder,
            self.maintenance_schedule_builder,
            self.specification_matrix_builder,
            self.performance_curve_builder,
        ):
            rendered = builder.build(table, chunk_type=chunk_type)
            if rendered:
                return rendered
        return self.generic_builder.build(table, chunk_type=chunk_type)
