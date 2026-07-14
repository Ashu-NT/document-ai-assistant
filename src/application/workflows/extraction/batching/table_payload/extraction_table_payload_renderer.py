from __future__ import annotations

from src.application.workflows.extraction.batching.table_payload.generic_table_payload_builder import (
    GenericTablePayloadBuilder,
)
from src.application.workflows.extraction.batching.table_payload.maintenance_schedule_payload_builder import (
    MaintenanceSchedulePayloadBuilder,
)
from src.application.workflows.extraction.batching.table_payload.performance_curve_payload_builder import (
    PerformanceCurvePayloadBuilder,
)
from src.application.workflows.extraction.batching.table_payload.specification_matrix_payload_builder import (
    SpecificationMatrixPayloadBuilder,
)
from src.domain.assets import TableAsset


class ExtractionTablePayloadRenderer:
    def __init__(
        self,
        *,
        maintenance_schedule_builder: (
            MaintenanceSchedulePayloadBuilder | None
        ) = None,
        specification_matrix_builder: (
            SpecificationMatrixPayloadBuilder | None
        ) = None,
        performance_curve_builder: PerformanceCurvePayloadBuilder | None = None,
        generic_builder: GenericTablePayloadBuilder | None = None,
    ) -> None:
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

    def render(self, table: TableAsset) -> str | None:
        for builder in (
            self.maintenance_schedule_builder,
            self.specification_matrix_builder,
            self.performance_curve_builder,
        ):
            rendered = builder.build(table)
            if rendered:
                return rendered
        return self.generic_builder.build(table)
