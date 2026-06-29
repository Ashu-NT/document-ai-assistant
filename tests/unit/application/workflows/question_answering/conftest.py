import pytest

from src.application.contracts.guardrails.confidence_level import ConfidenceLevel
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.services.answer_generation.answer_generation_result import (
    GeneratedAnswer,
)
from src.application.services.document_exploration.document_exploration_result import (
    DocumentCoverage,
    DocumentExplorationResult,
    DocumentOverview,
)
from src.application.services.document_exploration.document_exploration_service import (
    DocumentNotFoundError,
)
from src.application.workflows.retrieval.retrieval_workflow_result import (
    RetrievalWorkflowResult,
)
from src.domain.retrieval import RetrievalQuery, RetrievalResult
from src.domain.retrieval.citation import Citation


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class FakeRetrievalWorkflow:
    def __init__(self, result: RetrievalWorkflowResult) -> None:
        self._result = result
        self.called = False
        self.last_query: RetrievalQuery | None = None

    def run(self, query: RetrievalQuery, activity_context=None) -> RetrievalWorkflowResult:
        self.called = True
        self.last_query = query
        return self._result


class FakeDocumentExplorationService:
    def __init__(
        self,
        result: DocumentExplorationResult | None = None,
        raises: Exception | None = None,
    ) -> None:
        self._result = result
        self._raises = raises
        self.called_with: str | None = None

    def explore(self, document_id: str, activity_context=None) -> DocumentExplorationResult:
        self.called_with = document_id
        if self._raises is not None:
            raise self._raises
        assert self._result is not None
        return self._result


class FakeGuardrail:
    def __init__(
        self,
        *,
        allowed: bool,
        decision: GuardrailDecision,
        reason: str = "fake",
        safe_user_message: str | None = None,
        approved_chunk_ids: list[str] | None = None,
    ) -> None:
        self._result = GuardrailResult(
            decision=decision,
            allowed=allowed,
            reason=reason,
            confidence=ConfidenceLevel.HIGH,
            safe_user_message=safe_user_message,
            approved_chunk_ids=approved_chunk_ids or [],
        )

    def check(self, context: GuardrailContext) -> GuardrailResult:
        return self._result


class FakeAnswerGenerationService:
    def __init__(
        self,
        answer_text: str = "The filter must be replaced every 1000 hours.",
        citations: list[Citation] | None = None,
        answer_intent: AnswerIntent | None = None,
        raises: Exception | None = None,
    ) -> None:
        self._answer_text = answer_text
        self._citations = citations or []
        self._answer_intent = answer_intent
        self._raises = raises
        self.called_with: AnswerGenerationRequest | None = None

    def generate(self, request: AnswerGenerationRequest, activity_context=None) -> GeneratedAnswer:
        self.called_with = request
        if self._raises is not None:
            raise self._raises
        return GeneratedAnswer(
            answer_text=self._answer_text,
            citations=self._citations,
            cited_chunk_ids=[c.chunk_id for c in self._citations if c.chunk_id],
            prompt_version="v1",
            model_name="qwen3:8b",
            answer_intent=self._answer_intent,
            diagnostics=(
                {"answer_intent": self._answer_intent.value}
                if self._answer_intent is not None
                else {}
            ),
        )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_retrieval_query() -> RetrievalQuery:
    return RetrievalQuery(query_id="q_test", query_text="test question")


def _make_empty_retrieval_result(query: RetrievalQuery) -> RetrievalResult:
    return RetrievalResult(
        result_id="r_test",
        query=query,
        chunks=[],
        citations=[],
    )


@pytest.fixture()
def sample_retrieval_query() -> RetrievalQuery:
    return _make_retrieval_query()


@pytest.fixture()
def empty_workflow_result(sample_retrieval_query: RetrievalQuery) -> RetrievalWorkflowResult:
    return RetrievalWorkflowResult(
        retrieval_result=_make_empty_retrieval_result(sample_retrieval_query),
        enough_evidence=False,
        min_evidence_chunks=1,
        context_chunks=[],
    )


@pytest.fixture()
def sample_exploration_result() -> DocumentExplorationResult:
    overview = DocumentOverview(
        document_id="doc_001",
        title="Sample Manual",
        file_name="sample.pdf",
        document_type="manual",
        language="en",
        page_count=10,
        section_count=3,
        chunk_count=12,
        table_count=1,
        picture_count=0,
        identifier_count=2,
    )
    coverage = DocumentCoverage(
        chunk_type_counts={"general": 8, "overview": 4},
        has_tables=True,
        has_pictures=False,
        has_identifiers=True,
        has_sections=True,
    )
    return DocumentExplorationResult(
        document_id="doc_001",
        overview=overview,
        coverage=coverage,
    )


@pytest.fixture()
def fake_retrieval_workflow(
    empty_workflow_result: RetrievalWorkflowResult,
) -> FakeRetrievalWorkflow:
    return FakeRetrievalWorkflow(result=empty_workflow_result)


@pytest.fixture()
def fake_exploration_service(
    sample_exploration_result: DocumentExplorationResult,
) -> FakeDocumentExplorationService:
    return FakeDocumentExplorationService(result=sample_exploration_result)
