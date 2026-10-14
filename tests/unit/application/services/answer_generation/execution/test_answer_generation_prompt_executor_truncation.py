import json

import pytest

from src.application.contracts.ai import LLMGenerationResult
from src.application.services.answer_generation.answer_generation_response_parser import (
    AnswerGenerationResponseParser,
)
from src.application.services.answer_generation.execution.answer_generation_prompt_executor import (
    AnswerGenerationPromptExecutor,
)
from src.shared.exceptions import SchemaValidationError


class _FakeLLMService:
    def __init__(self, results: list[LLMGenerationResult]) -> None:
        self.results = list(results)
        self.calls = 0

    def generate_with_metadata(self, prompt, model=None, **kwargs):
        result = self.results[min(self.calls, len(self.results) - 1)]
        self.calls += 1
        return result


_VALID_JSON = json.dumps({"answer_text": "The interval is 1000 hours."})


def test_truncated_response_is_retried_then_raises_if_still_truncated() -> None:
    llm_service = _FakeLLMService(
        [
            LLMGenerationResult(text="{", provider_name="fake", finish_reason="length"),
            LLMGenerationResult(text="{", provider_name="fake", finish_reason="length"),
        ]
    )
    executor = AnswerGenerationPromptExecutor(
        llm_service=llm_service,
        response_parser=AnswerGenerationResponseParser(),
        model_name="qwen2.5:3b",
        temperature=0.2,
        num_ctx=8192,
    )

    with pytest.raises(SchemaValidationError):
        executor.execute("prompt")

    assert llm_service.calls == 2


def test_truncated_first_attempt_succeeds_on_retry() -> None:
    llm_service = _FakeLLMService(
        [
            LLMGenerationResult(text="{", provider_name="fake", finish_reason="length"),
            LLMGenerationResult(text=_VALID_JSON, provider_name="fake", finish_reason="stop"),
        ]
    )
    executor = AnswerGenerationPromptExecutor(
        llm_service=llm_service,
        response_parser=AnswerGenerationResponseParser(),
        model_name="qwen2.5:3b",
        temperature=0.2,
        num_ctx=8192,
    )

    result = executor.execute("prompt")

    assert result.parsed_output.answer_text == "The interval is 1000 hours."
    assert llm_service.calls == 2


def test_complete_response_is_accepted_without_retry() -> None:
    llm_service = _FakeLLMService(
        [LLMGenerationResult(text=_VALID_JSON, provider_name="fake", finish_reason="stop")]
    )
    executor = AnswerGenerationPromptExecutor(
        llm_service=llm_service,
        response_parser=AnswerGenerationResponseParser(),
        model_name="qwen2.5:3b",
        temperature=0.2,
        num_ctx=8192,
    )

    result = executor.execute("prompt")

    assert result.parsed_output.answer_text == "The interval is 1000 hours."
    assert llm_service.calls == 1
