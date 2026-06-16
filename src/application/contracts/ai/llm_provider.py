from typing import Protocol


class LLMProvider(Protocol):
    def generate(self, prompt: str, model: str | None = None) -> str:
        ...