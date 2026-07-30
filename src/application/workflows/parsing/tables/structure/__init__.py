from typing import TYPE_CHECKING

__all__ = [
    "TableHeaderPathBuilder",
    "TableShapeResolver",
    "TableStructureContextRenderer",
    "TableStructureSummary",
    "TableStructureSummaryBuilder",
]

if TYPE_CHECKING:
    from src.application.workflows.parsing.tables.structure.table_header_path_builder import (
        TableHeaderPathBuilder,
    )
    from src.application.workflows.parsing.tables.structure.table_shape_resolver import (
        TableShapeResolver,
    )
    from src.application.workflows.parsing.tables.structure.table_structure_context_renderer import (
        TableStructureContextRenderer,
    )
    from src.application.workflows.parsing.tables.structure.table_structure_summary import (
        TableStructureSummary,
    )
    from src.application.workflows.parsing.tables.structure.table_structure_summary_builder import (
        TableStructureSummaryBuilder,
    )


def __getattr__(name: str):
    if name == "TableHeaderPathBuilder":
        from src.application.workflows.parsing.tables.structure.table_header_path_builder import (
            TableHeaderPathBuilder,
        )

        return TableHeaderPathBuilder
    if name == "TableShapeResolver":
        from src.application.workflows.parsing.tables.structure.table_shape_resolver import (
            TableShapeResolver,
        )

        return TableShapeResolver
    if name == "TableStructureContextRenderer":
        from src.application.workflows.parsing.tables.structure.table_structure_context_renderer import (
            TableStructureContextRenderer,
        )

        return TableStructureContextRenderer
    if name == "TableStructureSummary":
        from src.application.workflows.parsing.tables.structure.table_structure_summary import (
            TableStructureSummary,
        )

        return TableStructureSummary
    if name == "TableStructureSummaryBuilder":
        from src.application.workflows.parsing.tables.structure.table_structure_summary_builder import (
            TableStructureSummaryBuilder,
        )

        return TableStructureSummaryBuilder
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
