from typing import Protocol


class LLMProvider(Protocol):
    def generate(
        self,
        prompt: str,
        model: str | None = None,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
    ) -> str:
        ...