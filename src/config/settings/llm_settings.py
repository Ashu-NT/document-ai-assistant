from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class LLMSettings(AppBaseSettings):
    ollama_base_url: str = Field(alias="OLLAMA_BASE_URL")

    general_llm: str = Field(alias="GENERAL_LLM")
    classification_llm: str = Field(alias="CLASSIFICATION_LLM")
    question_generation_llm: str = Field(alias="QUESTION_GENERATION_LLM")
    extraction_llm: str = Field(alias="EXTRACTION_LLM")
    answer_generation_llm: str | None = Field(default=None, alias="ANSWER_GENERATION_LLM")
    planning_llm: str | None = Field(default=None, alias="PLANNING_LLM")

    # Grounded QA wants low-variance, mostly-deterministic output rather
    # than running at whatever the Ollama model's bare sampling default
    # happens to be (finding 3.2) -- deliberately not reusing
    # extraction_temperature since extraction and answer generation have
    # different quality tradeoffs.
    answer_generation_temperature: float = Field(
        default=0.2, alias="ANSWER_GENERATION_TEMPERATURE"
    )
    # Bounded context window for the answer-generation call only -- a
    # reasonable middle ground, not exotic (finding 3.6). None/unset
    # elsewhere in this provider is unaffected; this is purely additive.
    answer_generation_num_ctx: int = Field(
        default=8192, alias="ANSWER_GENERATION_NUM_CTX"
    )
    # Default-off diagnostics capture of the exact prompt text sent to the
    # model (finding 3.5) -- gated so normal responses don't bloat with the
    # full prompt by default.
    capture_answer_prompt_text: bool = Field(
        default=False, alias="CAPTURE_ANSWER_PROMPT_TEXT"
    )

