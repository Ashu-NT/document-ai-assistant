from pydantic import Field

from src.config.settings.base_settings import AppBaseSettings


class PromptContextSettings(AppBaseSettings):
    max_items_per_array: int = Field(
        default=20,
        alias="PROMPT_CONTEXT_MAX_ITEMS_PER_ARRAY",
    )

    include_source_table_rows: bool = Field(
        default=False,
        alias="PROMPT_CONTEXT_INCLUDE_SOURCE_TABLE_ROWS",
    )

    max_table_rows_per_source: int = Field(
        default=20,
        alias="PROMPT_CONTEXT_MAX_TABLE_ROWS_PER_SOURCE",
    )

    # Bounds `PromptTableView.rows` in the top-level `tables` array -- a
    # separate knob from `max_table_rows_per_source` above, which only
    # applies to the opt-in (default-off) per-source `table_rows` fallback.
    # Without this, a single large table's rows serialized in full even
    # though every other array in the payload is capped (finding F7,
    # outputs/architecture/answering_and_prompt_fresh_audit.md).
    max_rows_per_table: int = Field(
        default=20,
        alias="PROMPT_CONTEXT_MAX_ROWS_PER_TABLE",
    )
