from __future__ import annotations

from typing import Any

from src.application.workflows.parsing.normalizers.table_rows.docling_table_row_repairer import (
    DoclingTableRowRepairer,
)
from src.application.workflows.parsing.normalizers.table_layout.parallel_streams.docling_parallel_table_reconstructor import (
    DoclingParallelTableReconstructor,
)
from src.application.workflows.parsing.normalizers.table_layout.docling_parallel_toc_reconstructor import (
    DoclingParallelTocReconstructor,
)
from src.application.workflows.parsing.normalizers.table_layout.docling_table_cell_candidate_builder import (
    DoclingTableCellCandidateBuilder,
)
from src.application.workflows.parsing.normalizers.table_layout.parallel_streams.docling_table_raw_row_builder import (
    DoclingTableRawRowBuilder,
)
from src.application.workflows.parsing.normalizers.table_layout.table_reconstruction_result import (
    TableReconstructionResult,
)
from src.domain.assets import TableCellSpan


class DoclingTableRowGridBuilder:
    """Builds a best-effort row grid from Docling table cell spans."""

    def __init__(
        self,
        *,
        cell_candidate_builder: DoclingTableCellCandidateBuilder | None = None,
        parallel_table_reconstructor: DoclingParallelTableReconstructor | None = None,
        parallel_toc_reconstructor: DoclingParallelTocReconstructor | None = None,
        raw_row_builder: DoclingTableRawRowBuilder | None = None,
        row_repairer: DoclingTableRowRepairer | None = None,
    ) -> None:
        self.cell_candidate_builder = (
            cell_candidate_builder or DoclingTableCellCandidateBuilder()
        )
        self.raw_row_builder = raw_row_builder or DoclingTableRawRowBuilder()
        self.row_repairer = row_repairer or DoclingTableRowRepairer()
        self.parallel_table_reconstructor = (
            parallel_table_reconstructor
            or DoclingParallelTableReconstructor(
                raw_row_builder=self.raw_row_builder,
                row_repairer=self.row_repairer,
            )
        )
        self.parallel_toc_reconstructor = (
            parallel_toc_reconstructor
            or DoclingParallelTocReconstructor(
                raw_row_builder=self.raw_row_builder,
            )
        )

    def build_reconstruction(
        self,
        spans: list[TableCellSpan],
        *,
        page_lane_count: int | None = None,
    ) -> TableReconstructionResult:
        if not spans:
            return TableReconstructionResult(rows=[], cell_spans=[])

        rows = self.parallel_toc_reconstructor.reconstruct(spans)
        if rows is not None:
            return TableReconstructionResult(rows=rows, cell_spans=spans)

        parallel_result = self.parallel_table_reconstructor.reconstruct(
            spans, page_lane_count=page_lane_count
        )
        if parallel_result is not None:
            parallel_result.cell_spans = spans
            return parallel_result

        raw_rows = self.raw_row_builder.build_rows(spans)
        return TableReconstructionResult(
            rows=self.row_repairer.repair_rows(raw_rows, cell_spans=spans),
            cell_spans=spans,
        )

    def build_rows(self, table_cells: list[Any]) -> list[list[str]]:
        spans = self.cell_candidate_builder.build(table_cells)
        return self.build_reconstruction(spans).rows
