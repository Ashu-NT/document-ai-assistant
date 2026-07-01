from typing import Any, Protocol


class LLMProvider(Protocol):
    def generate(
        self,
        prompt: str,
        model: str | None = None,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
        response_schema: dict[str, Any] | None = None,
    ) -> str:
        ...