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


def build_evaluation_run_metadata(
    *,
    parser_name: str | None = None,
    parser_version: str | None = None,
    conversion_fingerprint: str | None = None,
    evaluation_config: dict[str, Any] | None = None,
) -> EvaluationRunMetadata:
    return EvaluationRunMetadata(
        timestamp=datetime.now(timezone.utc).isoformat(),
        git_commit=resolve_git_commit(),
        artifact_schema_version=PARSED_ARTIFACT_SCHEMA_VERSION,
        parser_name=parser_name,
        parser_version=parser_version,
        conversion_fingerprint=conversion_fingerprint,
        evaluation_config=dict(evaluation_config or {}),
    )


__all__ = ["EvaluationRunMetadata", "build_evaluation_run_metadata"]
