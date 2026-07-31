from pydantic import Field

from src.config.settings.base_settings import AppBaseSettings


class ChunkingSettings(AppBaseSettings):
    # "transformer" measures real embedding-model subword tokens directly;
    # "whitespace" (word count) understates them for technical text, which
    # is why this was word-count-only for a while (with
    # ChunkingRuntimeFactory's safety clamp covering the gap). Every
    # size-sensitive threshold that assumed word counts (structured-family
    # min_tokens, front-matter detection, retrieval context_token_budget)
    # was audited and re-tuned or decoupled before this default flipped —
    # see end_to_end_pipeline_audit.md. "whitespace" remains available and
    # still truncation-safe via the clamp.
    token_counter_provider: str = Field(
        default="transformer",
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
