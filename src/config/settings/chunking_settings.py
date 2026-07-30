from pydantic import Field

from src.config.settings.base_settings import AppBaseSettings


class ChunkingSettings(AppBaseSettings):
    # "whitespace" (word count) understates real embedding-model subword
    # tokens for technical text; ChunkingRuntimeFactory's safety clamp
    # accounts for that gap so budgets stay truncation-safe regardless of
    # which counter is active. "transformer" measures real tokens directly
    # but changes chunk-size-sensitive behavior throughout the pipeline, so
    # it's opt-in rather than the default — see end_to_end_pipeline_audit.md.
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

    use_layout_front_matter_signal: bool = Field(
        default=False,
        alias="CHUNK_USE_LAYOUT_FRONT_MATTER_SIGNAL",
    )

    chunk_cross_reference_detection_enabled: bool = Field(
        default=False,
        alias="CHUNK_CROSS_REFERENCE_DETECTION_ENABLED",
    )
