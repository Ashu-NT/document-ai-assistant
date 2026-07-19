import pytest

from src.application.contracts.guardrails.guardrail_context import GuardrailContext

from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision

from src.application.contracts.guardrails.guardrail_result import GuardrailResult

from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation

from src.application.contracts.guardrails.violation_type import ViolationType

from src.application.guardrails.retrieval.query_scope_guardrail import QueryScopeGuardrail

from src.application.services.answer_generation.answer_generation_result import (
    AnswerSection,
    GeneratedAnswer,
    ReferenceNote,
)

from src.application.services.document_exploration.document_exploration_result import (
    DocumentExplorationResult,
)

from src.application.services.document_exploration.document_exploration_service import (
    DocumentNotFoundError,
)

from src.application.workflows.question_answering.question_answering_request import (
    QuestionAnsweringRequest,
)

from src.application.workflows.question_answering.question_answering_route import (
    QuestionAnsweringRoute,
)

from src.application.workflows.question_answering.question_answering_workflow import (
    QuestionAnsweringWorkflow,
)

from src.application.services.answer_generation.answer_generation_service import (
    AnswerGenerationService,
)

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)

from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    AnswerIntentAnalyzer,
)

from src.application.workflows.retrieval.retrieval_query_chunk_type_preference_mapper import (
    RetrievalQueryChunkTypePreferenceMapper,
)

from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)

from src.application.workflows.retrieval.retrieval_workflow_result import (
    RetrievalWorkflowResult,
)

from src.domain.common import ChunkType

from src.domain.common.source_location import SourceLocation

from src.domain.retrieval import RetrievalQuery, RetrievalResult

from src.domain.retrieval.citation import Citation

from src.domain.retrieval.retrieved_chunk import RetrievedChunk

from tests.unit.application.workflows.question_answering.conftest import (
    FakeAnswerGenerationService,
    FakeDocumentExplorationService,
    FakeDocumentLookupService,
    FakeGuardrail,
    FakeRetrievalWorkflow,
    FakeStructuredEvidenceResolver,
)

def make_workflow(
    fake_retrieval: FakeRetrievalWorkflow,
    fake_exploration: FakeDocumentExplorationService,
    pre_query_guardrails=None,
    context_guardrails=None,
    answer_generation_service=None,
    post_answer_guardrails=None,
    document_lookup_service=None,
    structured_evidence_resolver=None,
) -> QuestionAnsweringWorkflow:
    return QuestionAnsweringWorkflow(
        retrieval_workflow=fake_retrieval,
        exploration_service=fake_exploration,
        pre_query_guardrails=pre_query_guardrails,
        context_guardrails=context_guardrails,
        answer_generation_service=answer_generation_service,
        post_answer_guardrails=post_answer_guardrails,
        document_lookup_service=document_lookup_service,
        structured_evidence_resolver=structured_evidence_resolver,
    )

def _make_chunk(chunk_id: str = "chunk_001", citation: Citation | None = None) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=f"Technical content for {chunk_id}.",
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.GENERAL,
        section_path=["Section"],
        source=SourceLocation(page_start=1, page_end=1),
        citation=citation,
    )

def _make_retrieval_result_with_chunks(
    chunks: list[RetrievedChunk],
) -> RetrievalWorkflowResult:
    query = RetrievalQuery(query_id="q_test", query_text="test")
    result = RetrievalResult(result_id="r_test", query=query, chunks=chunks)
    return RetrievalWorkflowResult(
        retrieval_result=result,
        enough_evidence=True,
        min_evidence_chunks=1,
        context_chunks=chunks,
    )

class _CountingAnswerIntentAnalyzer(AnswerIntentAnalyzer):
    def __init__(self) -> None:
        super().__init__()
        self.call_count = 0

    def analyze(self, **kwargs):
        self.call_count += 1
        return super().analyze(**kwargs)

class _StubLLMService:
    def __init__(self, response: str) -> None:
        self._response = response

    def generate(self, prompt, model=None, **kwargs) -> str:
        return self._response

class _CapturingLLMService:
    def __init__(self, response: str) -> None:
        self._response = response
        self.prompts: list[str] = []

    def generate(self, prompt, model=None, **kwargs) -> str:
        self.prompts.append(prompt)
        return self._response

def test_final_result_carries_through_limitation_note_sections_and_reference_notes(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    """Plan section 9.6 (sections/reference_notes redesign): these three
    GeneratedAnswer fields must reach the final QuestionAnsweringResult --
    limitation_note was previously silently dropped here, and
    sections/reference_notes are new, so both are easy to forget."""
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)
    fake_gen = FakeAnswerGenerationService(
        limitation_note="Only the primary interval was found.",
        sections=[AnswerSection(heading="H", body="B", reference_note_ids=["r1"])],
        reference_notes=[
            ReferenceNote(note_id="r1", claim_text="c", source_number=1, chunk_id="chunk_001")
        ],
    )
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="What is the torque spec?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert result.limitation_note == "Only the primary interval was found."
    assert result.sections == [
        AnswerSection(heading="H", body="B", reference_note_ids=["r1"])
    ]
    assert result.reference_notes == [
        ReferenceNote(note_id="r1", claim_text="c", source_number=1, chunk_id="chunk_001")
    ]

def test_post_answer_guardrail_warnings_surface_in_diagnostics_without_blocking(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    """A guardrail result with a decision PR 11
    (answering_flow_weakness_remediation_plan.md) does not escalate (i.e.
    unmapped -- defaults to WARN) must not block the answer, but its
    violations must still reach diagnostics -- otherwise a warn-tier
    guardrail check would be computed and immediately discarded. (The
    escalated decisions -- UNSUPPORTED_CLAIMS/CITATION_REQUIRED/etc -- now
    regenerate-then-abstain instead; see the PR 11 tests below for those.)"""
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    warning_guardrail = FakeGuardrail(
        allowed=True,
        decision=GuardrailDecision.OUT_OF_SCOPE,
        reason="1 section(s) have no supporting reference notes.",
        violations=[
            GuardrailViolation(
                violation_type=ViolationType.UNSUPPORTED_CLAIM,
                description="Section 'H' has no reference notes supporting its content.",
                field="sections",
            )
        ],
    )
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        post_answer_guardrails=[warning_guardrail],
    )
    request = QuestionAnsweringRequest(
        question="What is the torque spec?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    warnings = result.diagnostics["post_answer_guardrail_warnings"]
    assert len(warnings) == 1
    assert warnings[0]["decision"] == GuardrailDecision.OUT_OF_SCOPE.value
    assert "no reference notes" in warnings[0]["violations"][0]


class _SequencedGuardrail:
    """A post-answer guardrail double that returns a different canned
    result on each successive `check()` call -- needed because
    `FakeGuardrail` always returns the same fixed result regardless of
    which answer it was given, and PR 11's regenerate-once loop needs to
    exercise "first check fails, second check (of the regenerated answer)
    passes/still fails" scenarios."""

    def __init__(self, results: list[GuardrailResult]) -> None:
        self._results = list(results)
        self.received_contexts: list[GuardrailContext] = []

    def check(self, context: GuardrailContext) -> GuardrailResult:
        self.received_contexts.append(context)
        index = min(len(self.received_contexts) - 1, len(self._results) - 1)
        return self._results[index]


class _SequencedAnswerGenerationService:
    """Returns a different canned `GeneratedAnswer` on each successive
    `generate()` call -- lets a test observe which attempt (original vs.
    the PR 11 regenerate) actually made it into the final result."""

    def __init__(self, answers: list[GeneratedAnswer]) -> None:
        self._answers = list(answers)
        self.calls = 0

    def generate(self, request, activity_context=None) -> GeneratedAnswer:
        answer = self._answers[min(self.calls, len(self._answers) - 1)]
        self.calls += 1
        return answer


def _generated(answer_text: str) -> GeneratedAnswer:
    return GeneratedAnswer(
        answer_text=answer_text,
        citations=[],
        cited_chunk_ids=[],
        prompt_version="v1",
        model_name="qwen3:8b",
    )


def test_post_answer_guardrail_regenerates_once_and_succeeds(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    """PR 11 (answering_flow_weakness_remediation_plan.md, closes W8): a
    REGENERATE-tier finding (e.g. CitationGuardrail's CITATION_REQUIRED)
    triggers exactly one regenerate attempt; if the regenerated answer
    passes, it -- not the original -- becomes the final result."""
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    guardrail = _SequencedGuardrail(
        [
            GuardrailResult(
                decision=GuardrailDecision.CITATION_REQUIRED,
                allowed=True,
                reason="Unresolved citation.",
            ),
            GuardrailResult(decision=GuardrailDecision.ALLOW, allowed=True, reason="ok"),
        ]
    )
    fake_gen = _SequencedAnswerGenerationService(
        [_generated("Original, uncited answer."), _generated("Regenerated, cited answer.")]
    )
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        post_answer_guardrails=[guardrail],
    )
    request = QuestionAnsweringRequest(
        question="What is the torque spec?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert fake_gen.calls == 2
    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert result.answer_text == "Regenerated, cited answer."
    assert result.diagnostics["post_answer_regenerated"] is True


def test_post_answer_guardrail_regenerates_once_then_abstains(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    """The regenerate-once cap: if the regenerated answer still fails, the
    turn abstains -- it does not try a second time."""
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    failing_result = GuardrailResult(
        decision=GuardrailDecision.CITATION_REQUIRED,
        allowed=True,
        reason="Unresolved citation.",
    )
    guardrail = _SequencedGuardrail([failing_result, failing_result])
    fake_gen = _SequencedAnswerGenerationService(
        [_generated("Original, uncited answer."), _generated("Still uncited answer.")]
    )
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        post_answer_guardrails=[guardrail],
    )
    request = QuestionAnsweringRequest(
        question="What is the torque spec?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert fake_gen.calls == 2
    assert result.route == QuestionAnsweringRoute.BLOCKED_BY_GUARDRAIL
    assert result.diagnostics["post_answer_disposition"] == "abstain"
    assert result.diagnostics["post_answer_regenerated"] is True
    assert "even after trying again" in result.safe_user_message


def test_post_answer_guardrail_abstains_immediately_for_a_safety_finding(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    """SafetyAnswerGuardrail's SAFETY_BLOCKED decision abstains immediately
    -- no regenerate attempt at all, per the sign-off decision (retrying a
    failed safety-evidence check risks confidently generating a
    *different* wrong answer)."""
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    guardrail = FakeGuardrail(
        allowed=True,
        decision=GuardrailDecision.SAFETY_BLOCKED,
        reason="Insufficient safety evidence.",
    )
    fake_gen = _SequencedAnswerGenerationService([_generated("Unverified safety answer.")])
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        post_answer_guardrails=[guardrail],
    )
    request = QuestionAnsweringRequest(
        question="What safety precautions apply?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert fake_gen.calls == 1
    assert result.route == QuestionAnsweringRoute.BLOCKED_BY_GUARDRAIL
    assert result.diagnostics["post_answer_disposition"] == "abstain"
    assert result.diagnostics["post_answer_regenerated"] is False
    assert "safety" in result.safe_user_message.lower()
    assert "even after trying again" not in result.safe_user_message


def test_post_answer_guardrail_requests_clarification_for_a_cross_document_conflict(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    """ConflictingEvidenceGuardrail's NEEDS_CLARIFICATION decision routes
    to QuestionAnsweringRoute.NEEDS_CLARIFICATION -- no regenerate, since a
    scope-ambiguity conflict isn't something another LLM pass can fix."""
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    guardrail = FakeGuardrail(
        allowed=True,
        decision=GuardrailDecision.NEEDS_CLARIFICATION,
        reason="Conflict spans multiple documents.",
        safe_user_message="Which equipment model do you mean?",
    )
    fake_gen = _SequencedAnswerGenerationService([_generated("The pressure is 6 bar or 8 bar.")])
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        post_answer_guardrails=[guardrail],
    )
    request = QuestionAnsweringRequest(
        question="What is the operating pressure?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert fake_gen.calls == 1
    assert result.route == QuestionAnsweringRoute.NEEDS_CLARIFICATION
    assert result.safe_user_message == "Which equipment model do you mean?"
    assert result.diagnostics["post_answer_disposition"] == "clarify"


def test_post_answer_guardrail_context_receives_sections_and_reference_notes_as_dicts(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    """GuardrailContext.sections/.reference_notes must be plain dicts, not
    the typed AnswerSection/ReferenceNote dataclasses -- matching the
    existing loose-dict convention `citations` already uses on that
    class, so guardrails/models never depends on application/services."""
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    spy_guardrail = FakeGuardrail(allowed=True, decision=GuardrailDecision.ALLOW)
    fake_gen = FakeAnswerGenerationService(
        sections=[AnswerSection(heading="H", body="B", reference_note_ids=["r1"])],
        reference_notes=[
            ReferenceNote(note_id="r1", claim_text="c", source_number=1, chunk_id="chunk_001")
        ],
    )
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        post_answer_guardrails=[spy_guardrail],
    )
    request = QuestionAnsweringRequest(
        question="What is the torque spec?",
        allow_answer_generation=True,
    )

    workflow.run(request)

    received = spy_guardrail.received_contexts[0]
    assert received.sections == [
        {"heading": "H", "body": "B", "reference_note_ids": ["r1"]}
    ]
    assert received.reference_notes == [
        {"note_id": "r1", "claim_text": "c", "source_number": 1, "chunk_id": "chunk_001"}
    ]

def test_approved_and_rejected_chunk_ids_are_accurate(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    chunk_a = _make_chunk("chunk_a")
    chunk_b = _make_chunk("chunk_b")
    chunk_c = _make_chunk("chunk_c")
    wf_result = _make_retrieval_result_with_chunks([chunk_a, chunk_b, chunk_c])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    # Context guardrail keeps chunk_a and chunk_b
    filtering_guardrail = FakeGuardrail(
        allowed=True,
        decision=GuardrailDecision.ALLOW,
        approved_chunk_ids=["chunk_a", "chunk_b"],
    )
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        context_guardrails=[filtering_guardrail],
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="What is the pressure?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert set(result.approved_chunk_ids) == {"chunk_a", "chunk_b"}
    assert result.rejected_chunk_ids == ["chunk_c"]
