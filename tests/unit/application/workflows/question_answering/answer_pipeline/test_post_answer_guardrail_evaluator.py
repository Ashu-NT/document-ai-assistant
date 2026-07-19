from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.guardrails.models.guardrail_disposition import (
    GuardrailDisposition,
)
from src.application.services.answer_generation.answer_generation_result import (
    AnswerSection,
    GeneratedAnswer,
    ReferenceNote,
)
from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.workflows.question_answering.answer_pipeline.post_answer_guardrail_evaluator import (
    PostAnswerGuardrailEvaluator,
)


class _FakeGuardrail:
    def __init__(self, result: GuardrailResult) -> None:
        self._result = result
        self.received_contexts = []

    def check(self, context):
        self.received_contexts.append(context)
        return self._result


def _generated(**overrides) -> GeneratedAnswer:
    defaults = dict(
        answer_text="Answer.",
        citations=[],
        cited_chunk_ids=[],
        prompt_version="v1",
        model_name="qwen3:8b",
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        sections=[AnswerSection(heading="H", body="B", reference_note_ids=["r1"])],
        reference_notes=[
            ReferenceNote(note_id="r1", claim_text="c", source_number=1, chunk_id="chunk_001")
        ],
        diagnostics={"coverage_requirement": "single_fact"},
    )
    defaults.update(overrides)
    return GeneratedAnswer(**defaults)


def test_evaluate_returns_pass_with_no_guardrails() -> None:
    evaluator = PostAnswerGuardrailEvaluator([])

    evaluation = evaluator.evaluate(
        generated=_generated(),
        question="What is the operating pressure?",
        analyzed_intent="specification",
        chunk_types=["technical_specification"],
        approved_chunks=[],
    )

    assert evaluation.disposition == GuardrailDisposition.PASS
    assert evaluation.driving_result is None
    assert evaluation.warnings == []


def test_evaluate_builds_context_with_plain_dict_sections_and_notes() -> None:
    guardrail = _FakeGuardrail(
        GuardrailResult(decision=GuardrailDecision.ALLOW, allowed=True, reason="ok")
    )
    evaluator = PostAnswerGuardrailEvaluator([guardrail])

    evaluator.evaluate(
        generated=_generated(),
        question="What is the operating pressure?",
        analyzed_intent="specification",
        chunk_types=["technical_specification"],
        approved_chunks=[],
    )

    context = guardrail.received_contexts[0]
    assert context.sections == [{"heading": "H", "body": "B", "reference_note_ids": ["r1"]}]
    assert context.reference_notes == [
        {"note_id": "r1", "claim_text": "c", "source_number": 1, "chunk_id": "chunk_001"}
    ]
    assert context.answer_intent == "specification_summary"
    assert context.metadata == {"coverage_requirement": "single_fact"}


def test_evaluate_derives_the_disposition_and_captures_warnings() -> None:
    guardrail = _FakeGuardrail(
        GuardrailResult(
            decision=GuardrailDecision.CITATION_REQUIRED,
            allowed=True,
            reason="Unresolved citation.",
        )
    )
    evaluator = PostAnswerGuardrailEvaluator([guardrail])

    evaluation = evaluator.evaluate(
        generated=_generated(),
        question="What is the operating pressure?",
        analyzed_intent="specification",
        chunk_types=["technical_specification"],
        approved_chunks=[],
    )

    assert evaluation.disposition == GuardrailDisposition.REGENERATE
    assert evaluation.driving_result.decision == GuardrailDecision.CITATION_REQUIRED
