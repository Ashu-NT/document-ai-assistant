from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class ExtractionSettings(AppBaseSettings):
    extraction_enabled: bool = Field(
        alias="EXTRACTION_ENABLED"
    )

    extraction_confidence_threshold: float = Field(
        alias="EXTRACTION_CONFIDENCE_THRESHOLD"
    )

    extraction_require_human_review: bool = Field(
        alias="EXTRACTION_REQUIRE_HUMAN_REVIEW"
    )
    extraction_max_chunks_per_batch: int = Field(
        default=8,
        alias="EXTRACTION_MAX_CHUNKS_PER_BATCH",
    )

    extraction_max_chars_per_batch: int = Field(
        default=8000,
        alias="EXTRACTION_MAX_CHARS_PER_BATCH",
    )

    extraction_allow_partial_batches: bool = Field(
        default=True,
        alias="EXTRACTION_ALLOW_PARTIAL_BATCHES",
    )

    extraction_failure_preview_chars: int = Field(
        default=1200,
        alias="EXTRACTION_FAILURE_PREVIEW_CHARS",
    )

    extraction_max_attempts: int = Field(
        default=2,
        alias="EXTRACTION_MAX_ATTEMPTS",
    )

    extraction_temperature: float = Field(
        default=0.0,
        alias="EXTRACTION_TEMPERATURE",
    )

    extraction_json_mode: bool = Field(
        default=True,
        alias="EXTRACTION_JSON_MODE",
    )

    identifier_extraction_enabled: bool = Field(
        default=True,
        alias="ENABLE_IDENTIFIER_EXTRACTION",
    )

    identifier_min_length: int = Field(
        default=3,
        alias="IDENTIFIER_MIN_LENGTH",
    )

    extraction_candidate_router_enabled: bool = Field(
        default=False,
        alias="EXTRACTION_CANDIDATE_ROUTER_ENABLED",
    )

    extraction_candidate_narrowing_enabled: bool = Field(
        default=False,
        alias="EXTRACTION_CANDIDATE_NARROWING_ENABLED",
    )

    semantic_linking_enabled: bool = Field(
        default=False,
        alias="SEMANTIC_LINKING_ENABLED",
    )

    # "multi_family" (default, current production behavior) or
    # "specialized_family" (experimental - see
    # ExtractionExecutionStrategy's docstring). A plain str here (not the
    # enum) to keep this settings module free of an application-layer
    # import; ExtractionWorkflow resolves it to the enum.
    extraction_execution_strategy: str = Field(
        default="multi_family",
        alias="EXTRACTION_EXECUTION_STRATEGY",
    )

    # PHASE 2B MAINTENANCE TABLE ROW-WINDOW EXTRACTION EXPERIMENT: default
    # OFF (production behavior unchanged). When enabled, a large structured
    # table under SPECIALIZED_FAMILY MaintenanceTask extraction is split
    # into bounded row windows (see TableEvidenceWindowBuilder /
    # TableWindowActivationPolicy) instead of one call covering every row.
    maintenance_table_window_enabled: bool = Field(
        default=False,
        alias="MAINTENANCE_TABLE_WINDOW_ENABLED",
    )
    maintenance_table_rows_per_window: int = Field(
        default=10,
        alias="MAINTENANCE_TABLE_ROWS_PER_WINDOW",
    )
