from __future__ import annotations

from typing import Any

from src.application.workflows.common.confidence_coercion import coerce_confidence_score
from src.application.workflows.extraction.context import SemanticExtractionContext
from src.application.workflows.extraction.response.parsing.extraction_payload_field_picker import (
    optional_payload_text,
    pick_payload_value,
)
from src.domain.common import SourceLocation
from src.domain.document import DocumentChunk
from src.domain.extraction import SemanticSourceMetadata
from src.shared.exceptions import SchemaValidationError

# Bookkeeping/field-access helpers genuinely shared by every per-entity
# builder in `builders/` -- payload field picking, required/optional text
# extraction, confidence-score parsing, source-chunk-id resolution
# (including recording invalid references for human review), source
# location, and semantic source metadata lookup. Split out of
# extraction_workflow.py's private helper methods rather than duplicated
# across the 11 per-entity builder files, per this file's ground rule 5.
#
# One instance is constructed per `ExtractionWorkflow` and threaded through
# every builder for that workflow's lifetime; `semantic_contexts` is
# (re)populated once per `extract()` call and `invalid_source_chunk_id_events`
# is reset once per batch, mirroring the mutable instance state
# `ExtractionWorkflow` used to hold directly before this split.


class ExtractionBuilderSupport:
    def __init__(
        self,
        *,
        confidence_threshold: float,
        require_human_review_default: bool,
    ) -> None:
        self.confidence_threshold = confidence_threshold
        self.require_human_review_default = require_human_review_default
        self.semantic_contexts: dict[str, SemanticExtractionContext] = {}
        self.invalid_source_chunk_id_events: list[dict[str, Any]] = []

    def set_semantic_contexts(
        self, semantic_contexts: dict[str, SemanticExtractionContext]
    ) -> None:
        self.semantic_contexts = semantic_contexts

    def reset_invalid_source_chunk_id_events(self) -> None:
        self.invalid_source_chunk_id_events = []

    @staticmethod
    def pick(payload: dict[str, Any], *keys: str) -> Any:
        return pick_payload_value(payload, *keys)

    @classmethod
    def required_text(
        cls,
        payload: dict[str, Any],
        *,
        field_name: str,
        keys: tuple[str, ...],
    ) -> str:
        value = cls.optional_text(payload, *keys)
        if value:
            return value

        raise SchemaValidationError(
            f"{field_name} is required.",
            details={field_name: payload},
        )

    @classmethod
    def optional_text(cls, payload: dict[str, Any], *keys: str) -> str | None:
        return optional_payload_text(payload, *keys)

    @staticmethod
    def parse_confidence(value: Any) -> float | None:
        return coerce_confidence_score(
            value,
            treat_bool_as_number=True,
            stringify_non_string_values=True,
        )

    @staticmethod
    def parse_bool(value: Any) -> bool | None:
        if value is None:
            return None

        if isinstance(value, bool):
            return value

        text = str(value).strip().lower()
        if text in {"true", "yes", "1"}:
            return True

        if text in {"false", "no", "0"}:
            return False

        return None

    def resolve_requires_human_review(
        self,
        raw_value: Any,
        confidence_score: float | None,
    ) -> bool:
        parsed_value = self.parse_bool(raw_value)
        if parsed_value is not None:
            return parsed_value

        if self.require_human_review_default:
            return True

        if confidence_score is None:
            return True

        return confidence_score < self.confidence_threshold

    def resolve_source_chunk_id(
        self,
        payload: dict[str, Any],
        *,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        item_type: str,
    ) -> tuple[str | None, bool]:
        source_chunk_id = self.optional_text(
            payload,
            "source_chunk_id",
            "chunk_id",
        )
        if source_chunk_id is None:
            return default_source_chunk_id, False

        if source_chunk_id not in chunk_lookup:
            self.invalid_source_chunk_id_events.append(
                {
                    "item_type": item_type,
                    "invalid_source_chunk_id": source_chunk_id,
                    "fallback_source_chunk_id": default_source_chunk_id,
                    "available_chunk_ids": list(chunk_lookup),
                }
            )
            return default_source_chunk_id, True

        return source_chunk_id, False

    @staticmethod
    def resolve_source_location(
        *,
        source_chunk_id: str | None,
        chunk_lookup: dict[str, DocumentChunk],
    ) -> SourceLocation:
        if source_chunk_id is None:
            return SourceLocation()

        chunk = chunk_lookup.get(source_chunk_id)
        if chunk is None:
            return SourceLocation()

        return SourceLocation(
            page_start=chunk.source.page_start,
            page_end=chunk.source.page_end,
            bbox=chunk.source.bbox,
        )

    def build_source_metadata(
        self,
        *,
        source_chunk_id: str | None,
        chunk_lookup: dict[str, DocumentChunk],
    ) -> SemanticSourceMetadata | None:
        if source_chunk_id is None:
            return None

        if source_chunk_id not in chunk_lookup:
            return None

        context = self.semantic_contexts.get(source_chunk_id)
        if context is None:
            return None

        return context.to_source_metadata()
