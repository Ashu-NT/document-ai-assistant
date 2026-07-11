from __future__ import annotations

from types import SimpleNamespace

from tests.unit.cli_scripts._test_cli_scripts_part1 import _load_script

from src.application.evaluation.answer_quality import GoldenAnswerCase
from src.application.tools.common import ToolResult


def _mod():
    return _load_script("run_answer_quality_judge")


def _case(**overrides) -> GoldenAnswerCase:
    defaults = dict(
        case_id="AQ-TEST",
        document_title="Test Document",
        question="What is the tank capacity?",
        expected_answer="The tank capacity is 1,200 L.",
        expected_claims=["Tank capacity is 1,200 L"],
        expected_citation_hint="the spec table",
    )
    defaults.update(overrides)
    return GoldenAnswerCase(**defaults)


class _FakeFindDocumentTool:
    def __init__(self, *, document_id: str | None = None, error_code: str | None = None):
        self.document_id = document_id
        self.error_code = error_code

    def run(self, request):
        if self.document_id is None:
            return ToolResult.fail(
                "Document was not found.",
                error_code=self.error_code or "document_not_found",
            )
        return ToolResult.ok(data={"document_id": self.document_id})


class _FakeAnswerQuestionTool:
    def __init__(self, *, find_document_tool=None, tool_result=None, raise_exc=None):
        self.find_document_tool = find_document_tool
        self._tool_result = tool_result
        self._raise_exc = raise_exc
        self.received_requests = []

    def run(self, request):
        self.received_requests.append(request)
        if self._raise_exc is not None:
            raise self._raise_exc
        return self._tool_result


class _FakeLLMService:
    def __init__(self, *, response: str | None = None, raise_exc=None):
        self._response = response
        self._raise_exc = raise_exc
        self.calls = []

    def generate(self, prompt, model=None, **kwargs):
        self.calls.append((prompt, model, kwargs))
        if self._raise_exc is not None:
            raise self._raise_exc
        return self._response


# --- parse_args -------------------------------------------------------


def test_parse_args_defaults():
    mod = _mod()
    args = mod.parse_args([])
    assert args.limit is None
    assert args.judge_model is None
    assert args.output is None


def test_parse_args_limit_and_judge_model_and_output():
    mod = _mod()
    args = mod.parse_args(
        ["--limit", "3", "--judge-model", "qwen2.5:7b", "--output", "out.json"]
    )
    assert args.limit == 3
    assert args.judge_model == "qwen2.5:7b"
    assert str(args.output) == "out.json"


# --- _build_judge_prompt ------------------------------------------------


def test_build_judge_prompt_includes_question_answer_and_claims():
    mod = _mod()
    prompt = mod._build_judge_prompt(
        question="What is the tank capacity?",
        answer_text="It is 1200 liters.",
        expected_answer="The tank capacity is 1,200 L.",
        expected_claims=["Tank capacity is 1,200 L", "Pump capacity is max 16,000 L/hr"],
    )
    assert "What is the tank capacity?" in prompt
    assert "It is 1200 liters." in prompt
    assert "The tank capacity is 1,200 L." in prompt
    assert "- Tank capacity is 1,200 L" in prompt
    assert "- Pump capacity is max 16,000 L/hr" in prompt
    assert "score" in prompt.lower()


# --- _parse_judge_response ----------------------------------------------


def test_parse_judge_response_plain_json():
    mod = _mod()
    score, justification = mod._parse_judge_response(
        '{"score": 0.75, "justification": "covers most claims"}'
    )
    assert score == 0.75
    assert justification == "covers most claims"


def test_parse_judge_response_strips_think_block_and_code_fence():
    mod = _mod()
    raw = (
        "<think>reasoning about the answer...</think>\n"
        '```json\n{"score": 1.0, "justification": "fully correct"}\n```'
    )
    score, justification = mod._parse_judge_response(raw)
    assert score == 1.0
    assert justification == "fully correct"


def test_parse_judge_response_clamps_out_of_range_score():
    mod = _mod()
    score, _ = mod._parse_judge_response('{"score": 1.7, "justification": "x"}')
    assert score == 1.0

    score, _ = mod._parse_judge_response('{"score": -0.3, "justification": "x"}')
    assert score == 0.0


def test_parse_judge_response_raises_on_unparseable_text():
    mod = _mod()
    try:
        mod._parse_judge_response("not json at all")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_parse_judge_response_raises_on_missing_score():
    mod = _mod()
    try:
        mod._parse_judge_response('{"justification": "no score field"}')
        assert False, "expected ValueError"
    except ValueError:
        pass


# --- generate_case_answer ------------------------------------------------


def test_generate_case_answer_success():
    mod = _mod()
    tool = _FakeAnswerQuestionTool(
        tool_result=ToolResult.ok(data=SimpleNamespace(answer_text="Tank capacity is 1200L."))
    )
    attempt = mod.generate_case_answer(
        answer_question_tool=tool,
        document_id="doc_1",
        question="What is the tank capacity?",
    )
    assert attempt.ok is True
    assert attempt.answer_text == "Tank capacity is 1200L."
    assert len(tool.received_requests) == 1


def test_generate_case_answer_tool_failure():
    mod = _mod()
    tool = _FakeAnswerQuestionTool(
        tool_result=ToolResult.fail("boom", error_code="generation_not_configured")
    )
    attempt = mod.generate_case_answer(
        answer_question_tool=tool,
        document_id="doc_1",
        question="Q?",
    )
    assert attempt.ok is False
    assert "generation_not_configured" in attempt.failure_reason


def test_generate_case_answer_empty_answer_text_is_a_failure():
    mod = _mod()
    tool = _FakeAnswerQuestionTool(
        tool_result=ToolResult.ok(data=SimpleNamespace(answer_text=""))
    )
    attempt = mod.generate_case_answer(
        answer_question_tool=tool,
        document_id="doc_1",
        question="Q?",
    )
    assert attempt.ok is False
    assert attempt.failure_reason == "empty_answer_text"


def test_generate_case_answer_application_error_is_caught():
    mod = _mod()
    from src.shared.exceptions import LLMProviderError

    tool = _FakeAnswerQuestionTool(
        raise_exc=LLMProviderError("Ollama unreachable", details={})
    )
    attempt = mod.generate_case_answer(
        answer_question_tool=tool,
        document_id="doc_1",
        question="Q?",
    )
    assert attempt.ok is False
    assert "Ollama unreachable" in attempt.failure_reason


# --- judge_answer ---------------------------------------------------------


def test_judge_answer_success():
    mod = _mod()
    llm_service = _FakeLLMService(
        response='{"score": 0.9, "justification": "covers all claims"}'
    )
    verdict = mod.judge_answer(
        judge_llm_service=llm_service,
        judge_model="qwen2.5:3b",
        question="Q?",
        answer_text="A.",
        expected_answer="A.",
        expected_claims=["claim one"],
    )
    assert verdict.ok is True
    assert verdict.score == 0.9
    assert verdict.justification == "covers all claims"
    assert llm_service.calls[0][1] == "qwen2.5:3b"


def test_judge_answer_llm_failure_is_reported_not_raised():
    mod = _mod()
    from src.shared.exceptions import LLMProviderError

    llm_service = _FakeLLMService(raise_exc=LLMProviderError("no ollama", details={}))
    verdict = mod.judge_answer(
        judge_llm_service=llm_service,
        judge_model=None,
        question="Q?",
        answer_text="A.",
        expected_answer="A.",
        expected_claims=["claim one"],
    )
    assert verdict.ok is False
    assert "no ollama" in verdict.failure_reason


def test_judge_answer_unparseable_response_is_reported_not_raised():
    mod = _mod()
    llm_service = _FakeLLMService(response="garbage, not json")
    verdict = mod.judge_answer(
        judge_llm_service=llm_service,
        judge_model=None,
        question="Q?",
        answer_text="A.",
        expected_answer="A.",
        expected_claims=["claim one"],
    )
    assert verdict.ok is False
    assert verdict.failure_reason is not None


# --- run_case / run_golden_set orchestration ------------------------------


def test_run_case_document_not_found_is_skipped():
    mod = _mod()
    find_document_tool = _FakeFindDocumentTool(document_id=None)
    answer_question_tool = _FakeAnswerQuestionTool(find_document_tool=find_document_tool)
    case_report = mod.run_case(
        _case(),
        answer_question_tool=answer_question_tool,
        judge_llm_service=_FakeLLMService(),
        judge_model=None,
    )
    assert case_report.status == mod._STATUS_DOCUMENT_NOT_FOUND
    assert case_report.score is None


def test_run_case_full_success_path():
    mod = _mod()
    find_document_tool = _FakeFindDocumentTool(document_id="doc_1")
    answer_question_tool = _FakeAnswerQuestionTool(
        find_document_tool=find_document_tool,
        tool_result=ToolResult.ok(
            data=SimpleNamespace(answer_text="The tank capacity is 1,200 L.")
        ),
    )
    llm_service = _FakeLLMService(
        response='{"score": 1.0, "justification": "matches the reference exactly"}'
    )
    case_report = mod.run_case(
        _case(),
        answer_question_tool=answer_question_tool,
        judge_llm_service=llm_service,
        judge_model="qwen2.5:3b",
    )
    assert case_report.status == mod._STATUS_JUDGED
    assert case_report.score == 1.0
    assert case_report.justification == "matches the reference exactly"


def test_run_golden_set_aggregates_average_score():
    mod = _mod()
    find_document_tool = _FakeFindDocumentTool(document_id="doc_1")
    answer_question_tool = _FakeAnswerQuestionTool(
        find_document_tool=find_document_tool,
        tool_result=ToolResult.ok(data=SimpleNamespace(answer_text="An answer.")),
    )

    responses = iter(
        [
            '{"score": 1.0, "justification": "great"}',
            '{"score": 0.5, "justification": "partial"}',
        ]
    )

    class _SequencedLLMService:
        def generate(self, prompt, model=None, **kwargs):
            return next(responses)

    cases = [_case(case_id="AQ-1"), _case(case_id="AQ-2")]
    report = mod.run_golden_set(
        cases,
        answer_question_tool=answer_question_tool,
        judge_llm_service=_SequencedLLMService(),
        judge_model=None,
    )
    assert len(report.cases) == 2
    assert len(report.judged_cases) == 2
    assert report.average_score == 0.75

    report_dict = report.to_dict()
    assert report_dict["judged_count"] == 2
    assert report_dict["average_score"] == 0.75


def test_run_golden_set_average_score_is_none_when_nothing_judged():
    mod = _mod()
    find_document_tool = _FakeFindDocumentTool(document_id=None)
    answer_question_tool = _FakeAnswerQuestionTool(find_document_tool=find_document_tool)
    report = mod.run_golden_set(
        [_case()],
        answer_question_tool=answer_question_tool,
        judge_llm_service=_FakeLLMService(),
        judge_model=None,
    )
    assert report.average_score is None
