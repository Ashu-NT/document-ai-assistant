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

  
    answer_generation_temperature: float = Field(
        default=0.2, alias="ANSWER_GENERATION_TEMPERATURE"
    )
    # Bounded context window for the answer-generation call only -- a
    # reasonable middle ground, not exotic (finding 3.6). None/unset
    # elsewhere in this provider is unaffected; this is purely additive.
    answer_generation_num_ctx: int = Field(
        default=8192, alias="ANSWER_GENERATION_NUM_CTX"
    )

    capture_answer_prompt_text: bool = Field(
        default=False, alias="CAPTURE_ANSWER_PROMPT_TEXT"
    )

    ollama_connect_timeout_seconds: float = Field(
        default=10.0, alias="OLLAMA_CONNECT_TIMEOUT_SECONDS", gt=0
    )
    ollama_read_timeout_seconds: float = Field(
        default=600.0, alias="OLLAMA_READ_TIMEOUT_SECONDS", gt=0
    )
    ollama_write_timeout_seconds: float = Field(
        default=10.0, alias="OLLAMA_WRITE_TIMEOUT_SECONDS", gt=0
    )
    ollama_pool_timeout_seconds: float = Field(
        default=10.0, alias="OLLAMA_POOL_TIMEOUT_SECONDS", gt=0
    )

    ollama_answer_max_output_tokens: int = Field(
        default=1024, alias="OLLAMA_ANSWER_MAX_OUTPUT_TOKENS", gt=0, le=32_768
    )
    ollama_question_generation_max_output_tokens: int = Field(
        default=1024, alias="OLLAMA_QUESTION_GENERATION_MAX_OUTPUT_TOKENS", gt=0, le=32_768
    )
    ollama_classification_max_output_tokens: int = Field(
        default=512, alias="OLLAMA_CLASSIFICATION_MAX_OUTPUT_TOKENS", gt=0, le=32_768
    )

    ollama_answer_read_timeout_seconds: float = Field(
        default=120.0, alias="OLLAMA_ANSWER_READ_TIMEOUT_SECONDS", gt=0
    )

