from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.application.evaluation.reproducibility.git_metadata import resolve_git_commit
from src.application.workflows.parsing.artifact_store.parsed_artifact_key import (
    PARSED_ARTIFACT_SCHEMA_VERSION,
)


@dataclass(slots=True, frozen=True)
class EvaluationRunMetadata:
    """Enough context to reproduce a given evaluation report's results, or
    at least explain why it differs from an earlier one - never secrets or
    a full environment dump.

    The `*_model`/`retrieval_configuration` fields are extension points for
    the classification/extraction/retrieval/RAG evaluation layers Phase 1
    does not implement yet; they stay `None` here rather than being invented
    without a real producer.
    """

    timestamp: str
    git_commit: str | None
    artifact_schema_version: int | None = None
    parser_name: str | None = None
    parser_version: str | None = None
    conversion_fingerprint: str | None = None
    evaluation_config: dict[str, Any] = field(default_factory=dict)

    # Extension points for later phases.
    classification_model: str | None = None
    extraction_model: str | None = None
    embedding_model: str | None = None
    retrieval_configuration: dict[str, Any] | None = None

    # Populated by Phase 2A (classification golden evaluation). Kept on
    # this same metadata model rather than a second reproducibility
    # system - see approved Phase 2A instruction to extend
    # EvaluationRunMetadata, not invent a parallel one.
    classification_execution_mode: str | None = None
    classification_confidence_threshold: float | None = None
    classification_allow_reclassification: bool | None = None
    classification_use_cache: bool | None = None
    classification_prompt_version: str | None = None

    # Populated by Phase 2B (extraction golden evaluation). Kept on this
    # same metadata model rather than a second reproducibility system -
    # same convention as the Phase 2A fields above. `extraction_model`
    # (the pre-existing extension-point field) is the model actually used;
    # `extraction_prompt_version` records the real combined-extraction
    # prompt builder's version constant (note: production names this
    # constant `IDENTIFIER_EXTRACTION_PROMPT_VERSION` even though it is the
    # general combined-extraction prompt version - see
    # combined_extraction_prompt_builder.py - reported verbatim here rather
    # than silently renamed).
    extraction_execution_mode: str | None = None
    extraction_prompt_version: str | None = None
    extraction_temperature: float | None = None
    extraction_max_attempts: int | None = None
    extraction_allow_partial_batches: bool | None = None
    extraction_candidate_narrowing_enabled: bool | None = None
    extraction_confidence_threshold: float | None = None


def build_evaluation_run_metadata(
    *,
    parser_name: str | None = None,
    parser_version: str | None = None,
    conversion_fingerprint: str | None = None,
    evaluation_config: dict[str, Any] | None = None,
    classification_model: str | None = None,
    classification_execution_mode: str | None = None,
    classification_confidence_threshold: float | None = None,
    classification_allow_reclassification: bool | None = None,
    classification_use_cache: bool | None = None,
    classification_prompt_version: str | None = None,
    extraction_model: str | None = None,
    extraction_execution_mode: str | None = None,
    extraction_prompt_version: str | None = None,
    extraction_temperature: float | None = None,
    extraction_max_attempts: int | None = None,
    extraction_allow_partial_batches: bool | None = None,
    extraction_candidate_narrowing_enabled: bool | None = None,
    extraction_confidence_threshold: float | None = None,
) -> EvaluationRunMetadata:
    return EvaluationRunMetadata(
        timestamp=datetime.now(timezone.utc).isoformat(),
        git_commit=resolve_git_commit(),
        artifact_schema_version=PARSED_ARTIFACT_SCHEMA_VERSION,
        parser_name=parser_name,
        parser_version=parser_version,
        conversion_fingerprint=conversion_fingerprint,
        evaluation_config=dict(evaluation_config or {}),
        classification_model=classification_model,
        classification_execution_mode=classification_execution_mode,
        classification_confidence_threshold=classification_confidence_threshold,
        classification_allow_reclassification=classification_allow_reclassification,
        classification_use_cache=classification_use_cache,
        classification_prompt_version=classification_prompt_version,
        extraction_model=extraction_model,
        extraction_execution_mode=extraction_execution_mode,
        extraction_prompt_version=extraction_prompt_version,
        extraction_temperature=extraction_temperature,
        extraction_max_attempts=extraction_max_attempts,
        extraction_allow_partial_batches=extraction_allow_partial_batches,
        extraction_candidate_narrowing_enabled=extraction_candidate_narrowing_enabled,
        extraction_confidence_threshold=extraction_confidence_threshold,
    )


__all__ = ["EvaluationRunMetadata", "build_evaluation_run_metadata"]
