from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

from src.application.services.answer_generation.formatting.answer_format_policy_catalog import (
    build_policy_catalog,
)
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.config.logging import get_logger

if TYPE_CHECKING:
    from src.application.workflows.question_answering.answer_context import (
        StructuredAnswerContext,
    )

_logger = get_logger(__name__)

# Bumped whenever _POLICIES' entries change materially (new/changed
# instruction_lines, preferred_format, or intent coverage), OR whenever
# resolve()'s context-aware adjustment rules below change materially --
# mirrors ANSWER_INTENT_RULES_VERSION's convention, so a future
# answer-quality regression can be correlated against a specific
# policy-pack version.
ANSWER_FORMAT_POLICY_RULES_VERSION = "v2"

# Below this, an AnswerKeyValue's extraction confidence is treated as
# "low" by resolve()'s context-aware pass. Chosen below the two hardcoded
# deterministic-extraction baselines (KeyValueExtractor's 0.9) so the
# signal only fires for genuinely below-baseline values (e.g. a
# real, domain-derived Identifier.confidence_score), not the constant
# baseline every chunk-text-derived key-value already carries.
_LOW_CONFIDENCE_THRESHOLD = 0.8

_SPARSE_EVIDENCE_INSTRUCTION = (
    "Only a small number of sources were retrieved for this question; if "
    "the evidence is incomplete, say so explicitly instead of implying "
    "full coverage."
)
_LOW_CONFIDENCE_EVIDENCE_INSTRUCTION = (
    "Some extracted facts have lower extraction confidence; note "
    "explicitly if a specific value could not be fully confirmed from the "
    "sources."
)
_RICH_STRUCTURED_EVIDENCE_INSTRUCTION = (
    "Structured facts, linked entity relationships, or table rows are "
    "available for this answer; use their exact values instead of "
    "paraphrasing them."
)
_MULTI_DOCUMENT_EVIDENCE_INSTRUCTION = (
    "The evidence spans more than one document; indicate which document "
    "each fact comes from when it is not obvious from context."
)


@dataclass(slots=True, frozen=True)
class AnswerFormatPolicy:
    intent: AnswerIntent
    preferred_format: str
    include_table: bool
    include_bullets: bool
    include_steps: bool
    max_bullets: int | None
    response_label: str
    instruction_lines: tuple[str, ...]
    # Which resolve() context signals fired for this instance -- empty for
    # policies obtained via for_intent()/resolve() with no context. Surfaced
    # verbatim in AnswerGenerationService diagnostics so a context-aware
    # adjustment is observable, not just baked silently into the prompt.
    context_signals: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def for_intent(cls, intent: AnswerIntent) -> "AnswerFormatPolicy":
        return _POLICIES.get(intent, _POLICIES[AnswerIntent.GENERAL])

    @classmethod
    def resolve(
        cls,
        *,
        intent: AnswerIntent,
        structured_context: "StructuredAnswerContext | None" = None,
    ) -> "AnswerFormatPolicy":
        base = cls.for_intent(intent)
        if structured_context is None:
            return base

        signals = cls._context_signals(structured_context)
        instruction_lines = base.instruction_lines
        if signals["is_sparse_evidence"]:
            instruction_lines += (_SPARSE_EVIDENCE_INSTRUCTION,)
        if signals["has_low_confidence_evidence"]:
            instruction_lines += (_LOW_CONFIDENCE_EVIDENCE_INSTRUCTION,)
        if signals["has_rich_structured_evidence"]:
            instruction_lines += (_RICH_STRUCTURED_EVIDENCE_INSTRUCTION,)
        if signals["is_multi_document"]:
            instruction_lines += (_MULTI_DOCUMENT_EVIDENCE_INSTRUCTION,)

        resolved = replace(
            base,
            instruction_lines=instruction_lines,
            context_signals=signals,
        )
        if any(signals.values()):
            _logger.info(
                "answer_format_policy_context_adjusted intent=%s signals=%s "
                "rules_version=%s",
                intent.value,
                signals,
                ANSWER_FORMAT_POLICY_RULES_VERSION,
            )
        return resolved

    @staticmethod
    def _context_signals(
        structured_context: "StructuredAnswerContext",
    ) -> dict[str, bool]:
        document_ids = structured_context.diagnostics.get("document_ids", [])
        has_low_confidence_evidence = any(
            key_value.confidence is not None
            and key_value.confidence < _LOW_CONFIDENCE_THRESHOLD
            for key_value in structured_context.key_values
        )
        has_rich_structured_evidence = bool(
            structured_context.structured_entities
        ) or any(source.table_rows for source in structured_context.sources)
        return {
            "is_sparse_evidence": structured_context.source_count <= 1,
            "has_low_confidence_evidence": has_low_confidence_evidence,
            "has_rich_structured_evidence": has_rich_structured_evidence,
            "is_multi_document": len(document_ids) > 1,
        }


_POLICIES: dict[AnswerIntent, AnswerFormatPolicy] = build_policy_catalog(
    AnswerFormatPolicy
)
