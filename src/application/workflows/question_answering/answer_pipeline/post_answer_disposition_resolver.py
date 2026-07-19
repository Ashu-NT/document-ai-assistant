from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.application.guardrails.answering.post_answer_abstain_messages import (
    resolve_abstain_message,
)
from src.application.guardrails.models.guardrail_disposition import (
    GuardrailDisposition,
)
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.answer_generation_result import (
    GeneratedAnswer,
)
from src.application.workflows.question_answering.answer_pipeline.post_answer_guardrail_evaluator import (
    PostAnswerGuardrailEvaluation,
    PostAnswerGuardrailEvaluator,
)
from src.application.workflows.question_answering.question_answering_result import (
    QuestionAnsweringResult,
)
from src.application.workflows.question_answering.question_answering_route import (
    QuestionAnsweringRoute,
)


@dataclass(frozen=True, slots=True)
class PostAnswerDispositionOutcome:
    """Either `terminal_result` is set (the pipeline must return it
    immediately -- CLARIFY/ABSTAIN/BLOCK, or REGENERATE escalated to
    ABSTAIN) or it's `None` and the pipeline proceeds to build its normal
    RETRIEVAL_QA result from `generated`/`evaluation` (PASS/WARN, or
    REGENERATE that came back clean)."""

    terminal_result: QuestionAnsweringResult | None
    generated: GeneratedAnswer
    evaluation: PostAnswerGuardrailEvaluation
    regenerated_once: bool


class PostAnswerDispositionResolver:
    """Turns one `PostAnswerGuardrailEvaluation` into either a terminal
    `QuestionAnsweringResult` or a signal to proceed -- including the
    regenerate-once-then-abstain loop (PR 11,
    answering_flow_weakness_remediation_plan.md, closes W8). Extracted out
    of `AnswerGenerationPipeline.run()` to keep that method's own length
    manageable; owns no state beyond its two collaborators."""

    def __init__(
        self,
        *,
        evaluator: PostAnswerGuardrailEvaluator,
        answer_generation_service,
    ) -> None:
        self._evaluator = evaluator
        self._answer_generation_service = answer_generation_service

    def resolve(
        self,
        *,
        generated: GeneratedAnswer,
        evaluation: PostAnswerGuardrailEvaluation,
        gen_request: AnswerGenerationRequest,
        question: str,
        analyzed_intent: str,
        chunk_types: list[str],
        approved_chunks: list,
        common_result_kwargs: dict[str, Any],
    ) -> PostAnswerDispositionOutcome:
        regenerated_once = False
        if evaluation.disposition == GuardrailDisposition.REGENERATE:
            regenerated = self._answer_generation_service.generate(gen_request)
            retry_evaluation = self._evaluator.evaluate(
                generated=regenerated,
                question=question,
                analyzed_intent=analyzed_intent,
                chunk_types=chunk_types,
                approved_chunks=approved_chunks,
            )
            regenerated_once = True
            if retry_evaluation.disposition in (
                GuardrailDisposition.PASS,
                GuardrailDisposition.WARN,
            ):
                generated = regenerated
                evaluation = retry_evaluation
            else:
                # Capped at exactly one regenerate attempt -- a second
                # validation failure abstains, it does not loop, regardless
                # of what disposition the retry itself produced.
                driving_result = retry_evaluation.driving_result or evaluation.driving_result
                return PostAnswerDispositionOutcome(
                    terminal_result=QuestionAnsweringResult(
                        route=QuestionAnsweringRoute.BLOCKED_BY_GUARDRAIL,
                        safe_user_message=resolve_abstain_message(
                            driving_result, regenerated=True
                        ),
                        guardrail_decision=(
                            driving_result.decision
                            if driving_result is not None
                            else None
                        ),
                        guardrail_result=driving_result,
                        diagnostics={
                            "blocked_by": "post_answer_guardrail",
                            "post_answer_disposition": "abstain",
                            "post_answer_regenerated": True,
                        },
                        **common_result_kwargs,
                    ),
                    generated=generated,
                    evaluation=evaluation,
                    regenerated_once=regenerated_once,
                )

        if evaluation.disposition == GuardrailDisposition.CLARIFY:
            return PostAnswerDispositionOutcome(
                terminal_result=QuestionAnsweringResult(
                    route=QuestionAnsweringRoute.NEEDS_CLARIFICATION,
                    safe_user_message=_safe_user_message(evaluation),
                    guardrail_decision=_guardrail_decision(evaluation),
                    guardrail_result=evaluation.driving_result,
                    diagnostics={
                        "blocked_by": "post_answer_guardrail",
                        "post_answer_disposition": "clarify",
                    },
                    **common_result_kwargs,
                ),
                generated=generated,
                evaluation=evaluation,
                regenerated_once=regenerated_once,
            )

        if evaluation.disposition == GuardrailDisposition.BLOCK:
            # An allowed=False post-answer result -- an unconditional hard
            # block, matching the pre-PR-11 contract exactly (no message
            # templating, uses the guardrail's own safe_user_message as-is).
            return PostAnswerDispositionOutcome(
                terminal_result=QuestionAnsweringResult(
                    route=QuestionAnsweringRoute.BLOCKED_BY_GUARDRAIL,
                    safe_user_message=_safe_user_message(evaluation),
                    guardrail_decision=_guardrail_decision(evaluation),
                    guardrail_result=evaluation.driving_result,
                    diagnostics={"blocked_by": "post_answer_guardrail"},
                    **common_result_kwargs,
                ),
                generated=generated,
                evaluation=evaluation,
                regenerated_once=regenerated_once,
            )

        if evaluation.disposition == GuardrailDisposition.ABSTAIN:
            return PostAnswerDispositionOutcome(
                terminal_result=QuestionAnsweringResult(
                    route=QuestionAnsweringRoute.BLOCKED_BY_GUARDRAIL,
                    safe_user_message=resolve_abstain_message(
                        evaluation.driving_result, regenerated=regenerated_once
                    ),
                    guardrail_decision=_guardrail_decision(evaluation),
                    guardrail_result=evaluation.driving_result,
                    diagnostics={
                        "blocked_by": "post_answer_guardrail",
                        "post_answer_disposition": "abstain",
                        "post_answer_regenerated": regenerated_once,
                    },
                    **common_result_kwargs,
                ),
                generated=generated,
                evaluation=evaluation,
                regenerated_once=regenerated_once,
            )

        return PostAnswerDispositionOutcome(
            terminal_result=None,
            generated=generated,
            evaluation=evaluation,
            regenerated_once=regenerated_once,
        )


def _safe_user_message(evaluation: PostAnswerGuardrailEvaluation) -> str | None:
    return (
        evaluation.driving_result.safe_user_message
        if evaluation.driving_result is not None
        else None
    )


def _guardrail_decision(evaluation: PostAnswerGuardrailEvaluation):
    return (
        evaluation.driving_result.decision
        if evaluation.driving_result is not None
        else None
    )
