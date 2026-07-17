__all__ = [
    "LogicalTableFamilyAssignment",
    "LogicalTableFamilyResolver",
    "TableSemanticResolver",
    "TableHeaderSignatureBuilder",
]


def __getattr__(name: str):
    if name == "LogicalTableFamilyAssignment":
        from src.application.workflows.parsing.tables.logical_table_family_assignment import (
            LogicalTableFamilyAssignment,
        )

        return LogicalTableFamilyAssignment
    if name == "LogicalTableFamilyResolver":
        from src.application.workflows.parsing.tables.logical_table_family_resolver import (
            LogicalTableFamilyResolver,
        )

        return LogicalTableFamilyResolver
    if name == "TableSemanticResolver":
        from src.application.workflows.parsing.tables.table_semantic_resolver import (
            TableSemanticResolver,
        )

        return TableSemanticResolver
    if name == "TableHeaderSignatureBuilder":
        from src.application.workflows.parsing.tables.table_header_signature_builder import (
            TableHeaderSignatureBuilder,
        )

        return TableHeaderSignatureBuilder
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
