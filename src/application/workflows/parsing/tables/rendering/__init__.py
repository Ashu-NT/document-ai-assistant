__all__ = ["StructuredRowRenderer", "TableAssetStructuredTextRenderer"]


def __getattr__(name: str):
    if name == "StructuredRowRenderer":
        from src.application.workflows.parsing.tables.rendering.structured_row_renderer import (
            StructuredRowRenderer,
        )

        return StructuredRowRenderer
    if name == "TableAssetStructuredTextRenderer":
        from src.application.workflows.parsing.tables.rendering.table_asset_structured_text_renderer import (
            TableAssetStructuredTextRenderer,
        )

        return TableAssetStructuredTextRenderer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
