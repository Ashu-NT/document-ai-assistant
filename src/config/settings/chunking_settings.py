from pydantic import Field

from src.config.settings.base_settings import AppBaseSettings


class ChunkingSettings(AppBaseSettings):
    token_counter_provider: str = Field(
        default="whitespace",
        alias="CHUNK_TOKEN_COUNTER_PROVIDER",
    )

    tokenizer_model: str | None = Field(
        default=None,
        alias="CHUNK_TOKENIZER_MODEL",
    )

    tokenizer_local_only: bool = Field(
        default=True,
        alias="CHUNK_TOKENIZER_LOCAL_ONLY",
    )
