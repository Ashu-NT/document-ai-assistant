from typing import Any

from src.application.contracts.ai import LLMProvider
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action


class LLMService:
    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm_provider = llm_provider

    @tracked_action(
        action="ai.llm.generated",
        activity=True,
        audit=False,
        event=False,
    )
    def generate(
        self,
        prompt: str,
        model: str | None = None,
        activity_context: ActivityContext | None = None,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
        response_schema: dict[str, Any] | None = None,
    ) -> str:
        provider_kwargs: dict[str, Any] = {}
        if temperature is not None:
            provider_kwargs["temperature"] = temperature
        if json_mode:
            provider_kwargs["json_mode"] = json_mode
        if response_schema is not None:
            provider_kwargs["response_schema"] = response_schema
        return self.llm_provider.generate(prompt, model=model, **provider_kwargs)
