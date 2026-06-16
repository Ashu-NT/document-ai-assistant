from pydantic import Field
from pydantic_settings import BaseSettings


class MemorySettings(BaseSettings):
    enable_short_term_memory: bool = Field(
        alias="ENABLE_SHORT_TERM_MEMORY"
    )

    enable_long_term_memory: bool = Field(
        alias="ENABLE_LONG_TERM_MEMORY"
    )

    max_conversation_messages: int = Field(
        alias="MAX_CONVERSATION_MESSAGES"
    )

    class Config:
        env_file = ".env"
        