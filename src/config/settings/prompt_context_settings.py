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
