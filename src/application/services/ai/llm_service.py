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
    ) -> str:
        return self.llm_provider.generate(prompt, model=model)
