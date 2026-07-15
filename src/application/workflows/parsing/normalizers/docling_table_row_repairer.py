from __future__ import annotations

from src.application.workflows.parsing.normalizers.docling_interval_table_row_repairer import (
    DoclingIntervalTableRowRepairer,
)
from src.application.workflows.parsing.normalizers.docling_sparse_continuation_row_merger import (
    DoclingSparseContinuationRowMerger,
)
from src.application.workflows.parsing.normalizers.docling_repeated_cell_row_collapser import (
    DoclingRepeatedCellRowCollapser,
)
from src.application.workflows.parsing.normalizers.docling_single_column_structured_table_reconstructor import (
    DoclingSingleColumnStructuredTableReconstructor,
)
from src.application.workflows.parsing.normalizers.docling_template_duplicate_column_collapser import (
    DoclingTemplateDuplicateColumnCollapser,
)
from src.application.workflows.parsing.normalizers.docling_toc_table_row_reconstructor import (
    DoclingTocTableRowReconstructor,
)


class DoclingTableRowRepairer:
    def __init__(
        self,
        *,
        interval_repairer: DoclingIntervalTableRowRepairer | None = None,
        sparse_continuation_row_merger: DoclingSparseContinuationRowMerger | None = None,
        repeated_cell_row_collapser: DoclingRepeatedCellRowCollapser | None = None,
        single_column_reconstructor: (
            DoclingSingleColumnStructuredTableReconstructor | None
        ) = None,
        template_duplicate_column_collapser: (
            DoclingTemplateDuplicateColumnCollapser | None
        ) = None,
        toc_reconstructor: DoclingTocTableRowReconstructor | None = None,
    ) -> None:
        self.interval_repairer = interval_repairer or DoclingIntervalTableRowRepairer()
        self.sparse_continuation_row_merger = (
            sparse_continuation_row_merger or DoclingSparseContinuationRowMerger()
        )
        self.repeated_cell_row_collapser = (
            repeated_cell_row_collapser or DoclingRepeatedCellRowCollapser()
        )
        self.single_column_reconstructor = (
            single_column_reconstructor
            or DoclingSingleColumnStructuredTableReconstructor()
        )
        self.template_duplicate_column_collapser = (
            template_duplicate_column_collapser
            or DoclingTemplateDuplicateColumnCollapser()
        )
        self.toc_reconstructor = toc_reconstructor or DoclingTocTableRowReconstructor()

    def repair_rows(self, rows: list[list[str]]) -> list[list[str]]:
        reconstructed = self.toc_reconstructor.reconstruct(rows)
        reconstructed = self.single_column_reconstructor.reconstruct(reconstructed)
        reconstructed = self.repeated_cell_row_collapser.collapse(reconstructed)
        reconstructed = self.template_duplicate_column_collapser.collapse(reconstructed)
        reconstructed = self.sparse_continuation_row_merger.merge(reconstructed)
        return self.interval_repairer.repair(reconstructed)
