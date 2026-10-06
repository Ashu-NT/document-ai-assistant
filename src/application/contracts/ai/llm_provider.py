from typing import Any, Protocol

from src.application.contracts.ai.llm_generation_result import LLMGenerationResult


class LLMProvider(Protocol):
    def generate(
        self,
        prompt: str,
        model: str | None = None,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
        response_schema: dict[str, Any] | None = None,
        num_ctx: int | None = None,
    ) -> str:
        ...

    def generate_with_metadata(
        self,
        prompt: str,
        model: str | None = None,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
        response_schema: dict[str, Any] | None = None,
        num_ctx: int | None = None,
    ) -> LLMGenerationResult:
        ...
