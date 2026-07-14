from __future__ import annotations

from src.application.workflows.parsing.normalizers.docling_interval_table_row_repairer import (
    DoclingIntervalTableRowRepairer,
)
from src.application.workflows.parsing.normalizers.docling_repeated_cell_row_collapser import (
    DoclingRepeatedCellRowCollapser,
)
from src.application.workflows.parsing.normalizers.docling_single_column_structured_table_reconstructor import (
    DoclingSingleColumnStructuredTableReconstructor,
)
from src.application.workflows.parsing.normalizers.docling_toc_table_row_reconstructor import (
    DoclingTocTableRowReconstructor,
)


class DoclingTableRowRepairer:
    def __init__(
        self,
        *,
        interval_repairer: DoclingIntervalTableRowRepairer | None = None,
        repeated_cell_row_collapser: DoclingRepeatedCellRowCollapser | None = None,
        single_column_reconstructor: (
            DoclingSingleColumnStructuredTableReconstructor | None
        ) = None,
        toc_reconstructor: DoclingTocTableRowReconstructor | None = None,
    ) -> None:
        self.interval_repairer = interval_repairer or DoclingIntervalTableRowRepairer()
        self.repeated_cell_row_collapser = (
            repeated_cell_row_collapser or DoclingRepeatedCellRowCollapser()
        )
        self.single_column_reconstructor = (
            single_column_reconstructor
            or DoclingSingleColumnStructuredTableReconstructor()
        )
        self.toc_reconstructor = toc_reconstructor or DoclingTocTableRowReconstructor()

    def repair_rows(self, rows: list[list[str]]) -> list[list[str]]:
        reconstructed = self.toc_reconstructor.reconstruct(rows)
        reconstructed = self.single_column_reconstructor.reconstruct(reconstructed)
        reconstructed = self.repeated_cell_row_collapser.collapse(reconstructed)
        return self.interval_repairer.repair(reconstructed)
