from src.application.services.ai.llm_service import LLMService
from src.application.services.answer_generation.answer_generation_response_parser import (
    AnswerGenerationResponseParser,
)
from src.application.services.answer_generation.answer_generation_response_schema import (
    build_answer_generation_response_json_schema,
)
from src.application.services.answer_generation.execution.prompt_execution_result import (
    PromptExecutionResult,
)
from src.shared.exceptions import SchemaValidationError

_MAX_GENERATION_ATTEMPTS = 2


def _build_corrective_note(previous_error: str) -> str:
    return (
        "\n\nYour previous response was rejected because it did not match "
        f"the required schema: {previous_error}\n"
        "Fix this specific problem and return a corrected JSON response "
        "that matches the schema exactly."
    )


class AnswerGenerationPromptExecutor:
    def __init__(
        self,
        *,
        llm_service: LLMService,
        response_parser: AnswerGenerationResponseParser,
        model_name: str | None,
        temperature: float,
        num_ctx: int,
    ) -> None:
        self.llm_service = llm_service
        self.response_parser = response_parser
        self.model_name = model_name
        self.temperature = temperature
        self.num_ctx = num_ctx

    def execute(self, prompt: str) -> PromptExecutionResult:
        last_error: SchemaValidationError | None = None
        for attempt_index in range(1, _MAX_GENERATION_ATTEMPTS + 1):
            attempt_prompt = (
                prompt
                if last_error is None
                else prompt + _build_corrective_note(str(last_error))
            )
            raw_output = self.llm_service.generate(
                attempt_prompt,
                model=self.model_name,
                response_schema=build_answer_generation_response_json_schema(),
                temperature=self.temperature,
                num_ctx=self.num_ctx,
            )
            try:
                return PromptExecutionResult(
                    parsed_output=self.response_parser.parse(raw_output),
                    raw_output=raw_output,
                )
            except SchemaValidationError as exc:
                last_error = exc
                if attempt_index >= _MAX_GENERATION_ATTEMPTS:
                    raise
        raise last_error  # pragma: no cover
