__all__ = ["TableRowSemanticNormalizer"]


def __getattr__(name: str):
    if name == "TableRowSemanticNormalizer":
        from src.application.workflows.parsing.tables.normalization.table_row_semantic_normalizer import (
            TableRowSemanticNormalizer,
        )

        return TableRowSemanticNormalizer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
