from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.guardrails.answering.guardrail_disposition_mapper import (
    combine_post_answer_dispositions,
)
from src.application.guardrails.guardrail_runner import GuardrailRunner
from src.application.guardrails.models.guardrail_disposition import (
    GuardrailDisposition,
)
from src.application.services.answer_generation.answer_generation_result import (
    GeneratedAnswer,
)


@dataclass(frozen=True, slots=True)
class PostAnswerGuardrailEvaluation:
    disposition: GuardrailDisposition
    driving_result: GuardrailResult | None
    warnings: list[dict[str, Any]] = field(default_factory=list)


class PostAnswerGuardrailEvaluator:
    """Runs every post-answer guardrail against one generated answer and
    reduces the results to a single disposition (PR 11,
    answering_flow_weakness_remediation_plan.md, closes W8) -- the shared
    evaluation `AnswerGenerationPipeline.run()` calls once for the original
    answer and, when the disposition is REGENERATE, once more for the
    regenerated one."""

    def __init__(self, guardrails: list) -> None:
        self._guardrails = guardrails

    def evaluate(
        self,
        *,
        generated: GeneratedAnswer,
        question: str,
        analyzed_intent: str,
        chunk_types: list[str],
        approved_chunks: list,
    ) -> PostAnswerGuardrailEvaluation:
        if not self._guardrails:
            return PostAnswerGuardrailEvaluation(GuardrailDisposition.PASS, None)

        context = GuardrailContext(
            query_text=question,
            query_intent=analyzed_intent,
            query_chunk_types=chunk_types,
            approved_chunks=approved_chunks,
            answer_text=generated.answer_text,
            answer_intent=(
                generated.answer_intent.value
                if generated.answer_intent is not None
                else None
            ),
            # Converted to plain dicts here (not the typed
            # AnswerSection/ReferenceNote dataclasses) to match
            # GuardrailContext's existing loose-dict convention for
            # cross-layer data -- plan section 9.6 sections/reference_notes
            # redesign.
            sections=[
                {
                    "heading": section.heading,
                    "body": section.body,
                    "reference_note_ids": section.reference_note_ids,
                }
                for section in generated.sections
            ],
            reference_notes=[
                {
                    "note_id": note.note_id,
                    "claim_text": note.claim_text,
                    "source_number": note.source_number,
                    "chunk_id": note.chunk_id,
                }
                for note in generated.reference_notes
            ],
            metadata=generated.diagnostics,
        )
        results = GuardrailRunner(self._guardrails).run_all(context)
        disposition, driving_result = combine_post_answer_dispositions(results)
        warnings = [
            {
                "decision": result.decision.value,
                "reason": result.reason,
                "violations": [
                    violation.description for violation in result.violations
                ],
            }
            for result in results
            if result.violations
        ]
        return PostAnswerGuardrailEvaluation(disposition, driving_result, warnings)
