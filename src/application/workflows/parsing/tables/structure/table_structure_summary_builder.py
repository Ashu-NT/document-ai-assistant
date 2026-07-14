from __future__ import annotations

from src.application.workflows.parsing.tables.structure.maintenance_schedule_structure_summarizer import (
    MaintenanceScheduleStructureSummarizer,
)
from src.application.workflows.parsing.tables.structure.performance_curve_structure_summarizer import (
    PerformanceCurveStructureSummarizer,
)
from src.application.workflows.parsing.tables.structure.specification_matrix_structure_summarizer import (
    SpecificationMatrixStructureSummarizer,
)
from src.application.workflows.parsing.tables.structure.generic_record_structure_summarizer import (
    GenericRecordStructureSummarizer,
)
from src.application.workflows.parsing.tables.structure.table_structure_summary import (
    TableStructureSummary,
)
from src.domain.assets import TableAsset


class TableStructureSummaryBuilder:
    def __init__(
        self,
        *,
        maintenance_schedule_summarizer: (
            MaintenanceScheduleStructureSummarizer | None
        ) = None,
        performance_curve_summarizer: PerformanceCurveStructureSummarizer | None = None,
        specification_matrix_summarizer: (
            SpecificationMatrixStructureSummarizer | None
        ) = None,
        generic_record_summarizer: GenericRecordStructureSummarizer | None = None,
    ) -> None:
        self.maintenance_schedule_summarizer = (
            maintenance_schedule_summarizer
            or MaintenanceScheduleStructureSummarizer()
        )
        self.performance_curve_summarizer = (
            performance_curve_summarizer or PerformanceCurveStructureSummarizer()
        )
        self.specification_matrix_summarizer = (
            specification_matrix_summarizer
            or SpecificationMatrixStructureSummarizer()
        )
        self.generic_record_summarizer = (
            generic_record_summarizer or GenericRecordStructureSummarizer()
        )

    def build(self, table: TableAsset) -> TableStructureSummary | None:
        for summarizer in (
            self.maintenance_schedule_summarizer,
            self.performance_curve_summarizer,
            self.specification_matrix_summarizer,
        ):
            summary = summarizer.summarize(table.rows)
            if summary is not None:
                return summary
        return self.generic_record_summarizer.summarize(table)
