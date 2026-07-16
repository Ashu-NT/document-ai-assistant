from src.application.workflows.parsing.tables.semantics import (
    TableSemanticClassifier,
)
from src.application.workflows.parsing.tables.structure import TableStructureSummary
from src.application.workflows.shared.table_category import TableCategory
from src.application.workflows.shared.table_shape import TableShape
from src.domain.assets import TableAsset


def _make_table(rows: list[list[str]], *, markdown: str = "table") -> TableAsset:
    return TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown=markdown,
        rows=rows,
        row_count=len(rows),
        column_count=len(rows[0]) if rows else None,
    )


def test_classify_prefers_specification_shape_over_weak_spare_parts_markers() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table(
            [
                ["Position", "Qty", "Specification", "Year of Manufacture"],
                ["Drive", "1", "BF30", "2024"],
                ["Motor", "1", "3 kW", "2024"],
                ["Pump", "1", "16,000 L/hr", "2024"],
            ]
        ),
        section_path=["Technical Data", "Operating Fluid Systems"],
        structure_summary=TableStructureSummary(
            table_shape=TableShape.SPECIFICATION_MATRIX,
            quality_score=0.91,
        ),
    )

    assert category == TableCategory.TECHNICAL_DATA_TABLE
    assert confidence >= 0.8
