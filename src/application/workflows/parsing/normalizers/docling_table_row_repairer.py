from __future__ import annotations

from src.application.workflows.parsing.normalizers.docling_interval_table_row_repairer import (
    DoclingIntervalTableRowRepairer,
)
from src.application.workflows.parsing.normalizers.docling_single_column_structured_table_reconstructor import (
    DoclingSingleColumnStructuredTableReconstructor,
)


class DoclingTableRowRepairer:
    def __init__(
        self,
        *,
        interval_repairer: DoclingIntervalTableRowRepairer | None = None,
        single_column_reconstructor: (
            DoclingSingleColumnStructuredTableReconstructor | None
        ) = None,
    ) -> None:
        self.interval_repairer = interval_repairer or DoclingIntervalTableRowRepairer()
        self.single_column_reconstructor = (
            single_column_reconstructor
            or DoclingSingleColumnStructuredTableReconstructor()
        )

    def repair_rows(self, rows: list[list[str]]) -> list[list[str]]:
        reconstructed = self.single_column_reconstructor.reconstruct(rows)
        return self.interval_repairer.repair(reconstructed)
