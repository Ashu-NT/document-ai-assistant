from dataclasses import replace
from typing import TYPE_CHECKING

from src.application.prompts.answer_generation.prompt_context import (
    EvidenceSchemaFormatter,
    PromptContextProjector,
    RawSourceAppendixFormatter,
    StructuredEvidencePayloadSerializer,
)
from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
)
from src.application.prompts.answer_generation.answer_prompt_version import (
    ANSWER_PROMPT_VERSION,
)
from src.application.prompts.common import (
    ANSWER_GROUNDING_RULES,
    PromptMetadata,
)

if TYPE_CHECKING:
    from src.application.services.answer_generation.answer_generation_request import (
        AnswerGenerationRequest,
    )


class AnswerPromptBuilder:
    prompt_version = ANSWER_PROMPT_VERSION
    metadata = PromptMetadata(
        name="answer_generation",
        version=ANSWER_PROMPT_VERSION,
        task_type="answer_generation",
        model_type="llm",
        description="Grounded answer generation from retrieved document chunks.",
    )

    def __init__(
        self,
        prompt_context_projector: PromptContextProjector | None = None,
        evidence_schema_formatter: EvidenceSchemaFormatter | None = None,
        structured_evidence_payload_serializer: StructuredEvidencePayloadSerializer
        | None = None,
        raw_source_appendix_formatter: RawSourceAppendixFormatter | None = None,
    ) -> None:
        self.prompt_context_projector = (
            prompt_context_projector or PromptContextProjector()
        )
        self.evidence_schema_formatter = (
            evidence_schema_formatter or EvidenceSchemaFormatter()
        )
        self.structured_evidence_payload_serializer = (
            structured_evidence_payload_serializer
            or StructuredEvidencePayloadSerializer()
        )
        self.raw_source_appendix_formatter = (
            raw_source_appendix_formatter or RawSourceAppendixFormatter()
        )

    def build(self, request: "AnswerGenerationRequest") -> str:
        prompt, _context_bundle = self.build_with_context(request)
        return prompt

    def build_with_context(
        self, request: "AnswerGenerationRequest"
    ) -> tuple[str, PromptContextBundle | None]:
        """Same as `build()`, but also returns the `PromptContextBundle`
        this call produced -- which source_numbers were actually shown as
        raw prose (`appendix_source_numbers`) and the canonicalizer's own
        diagnostics counters (`.diagnostics`). Returning this per-call,
        rather than caching it on `self.last_context_bundle` (the previous
        design), removes unscoped mutable instance state that would have
        been a real concurrency hazard if this service were ever called
        from overlapping requests (finding F10,
        outputs/architecture/answering_and_prompt_fresh_audit.md) -- not an
        active bug under today's single-threaded CLI callers, but worth
        closing before, not after, any future concurrent API/UI backend."""
        prompt_context = self.prompt_context_projector.project(
            request.structured_context
        )
        evidence_schema = self.evidence_schema_formatter.format(prompt_context)
        structured_payload, payload_truncation_diagnostics = (
            self.structured_evidence_payload_serializer.serialize_with_diagnostics(
                prompt_context
            )
        )
        source_blocks, appendix_source_numbers, appendix_truncation_diagnostics = (
            self.raw_source_appendix_formatter.format_with_diagnostics(prompt_context)
        )
        if prompt_context is not None:
            prompt_context = replace(
                prompt_context,
                appendix_source_numbers=appendix_source_numbers,
                diagnostics={
                    **prompt_context.diagnostics,
                    **payload_truncation_diagnostics,
                    "raw_source_appendix_truncation": appendix_truncation_diagnostics,
                },
            )
        prompt = (
            f"{ANSWER_GROUNDING_RULES}\n\n"
            "Return JSON only with this shape:\n"
            '{\n  "answer_text": "<grounded answer>",\n'
            '  "limitation_note": "<optional: state explicitly what the '
            'provided sources do not cover, omit this field entirely if '
            'there is no limitation to report>",\n'
            '  "sections": [{"heading": "<short heading>", "body": '
            '"<section text>", "reference_note_ids": ["<id from '
            'reference_notes below>"]}],\n'
            '  "reference_notes": [{"note_id": "<short id you choose, e.g. '
            '\'r1\'>", "claim_text": "<the specific claim this note '
            'supports>", "source_number": <the SOURCE number below that '
            "supports this claim>}]\n}\n"
            'Only include "sections"/"reference_notes" when the answer '
            "naturally breaks into distinct topics or claims worth "
            "attributing individually; omit both entirely for a short, "
            "single-fact answer. `source_number` in reference_notes must "
            "be a number for a SOURCE shown below -- this is a structured "
            "field, not part of answer_text, so the grounding rule against "
            "referencing SOURCE labels in the answer does not apply to it.\n"
            "Do not wrap the JSON in markdown fences.\n\n"
            f"{self._intent_block(request)}"
            f"{self._format_policy_block(request)}"
            f"Question: {request.question}\n\n"
            f"{self._identifier_block(request)}"
        )
        if evidence_schema:
            prompt += evidence_schema
        if structured_payload:
            prompt += "Structured evidence payload:\n"
            prompt += f"{structured_payload}\n\n"
        if source_blocks:
            prompt += "Raw source appendix:\n"
            prompt += source_blocks
            prompt += "\n\n"
        prompt += (
            "Answer the question above using only the evidence shown: "
            f"{request.question}\n"
        )
        return prompt, prompt_context

    @staticmethod
    def _identifier_block(request: "AnswerGenerationRequest") -> str:
        identifiers = getattr(request, "resolved_identifiers", None)
        if not identifiers:
            return ""
        lines = ["Resolved identifiers:"]
        for identifier in identifiers:
            type_label = identifier.identifier_type.value.replace("_", " ").title()
            lines.append(
                f"- {type_label}: {identifier.raw_value}"
                f" (normalized: {identifier.normalized_value})"
            )
        return "\n".join(lines) + "\n\n"

    @staticmethod
    def _intent_block(request: "AnswerGenerationRequest") -> str:
        lines: list[str] = []
        if request.answer_intent is not None:
            lines.append(f"Answer intent: {request.answer_intent.value}")
        if request.retrieval_intent:
            lines.append(f"Retrieval intent: {request.retrieval_intent}")
        elif request.query_intent:
            lines.append(f"Legacy query intent: {request.query_intent}")
        if not lines:
            return ""
        return "\n".join(lines) + "\n\n"

    @staticmethod
    def _format_policy_block(request: "AnswerGenerationRequest") -> str:
        policy = request.format_policy
        if policy is None:
            return ""
        lines = [
            "Answer format policy:",
            f"- Preferred format: {policy.preferred_format}",
            f"- Response label: {policy.response_label}",
            f"- Include bullets: {'yes' if policy.include_bullets else 'no'}",
            f"- Include numbered steps: {'yes' if policy.include_steps else 'no'}",
            f"- Include table-like structure: {'yes' if policy.include_table else 'no'}",
        ]
        if policy.max_bullets is not None:
            lines.append(f"- Max bullets: {policy.max_bullets}")
        lines.append("Task instructions:")
        lines.extend(f"- {instruction}" for instruction in policy.instruction_lines)
        return "\n".join(lines) + "\n\n"

