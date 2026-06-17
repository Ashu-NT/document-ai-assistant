from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class MemorySettings(AppBaseSettings):
    enable_short_term_memory: bool = Field(
        alias="ENABLE_SHORT_TERM_MEMORY"
    )

    enable_long_term_memory: bool = Field(
        alias="ENABLE_LONG_TERM_MEMORY"
    )

    max_conversation_messages: int = Field(
        alias="MAX_CONVERSATION_MESSAGES"
    )
        