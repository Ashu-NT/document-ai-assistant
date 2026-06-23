from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class LLMSettings(AppBaseSettings):
    ollama_base_url: str = Field(alias="OLLAMA_BASE_URL")

    general_llm: str = Field(alias="GENERAL_LLM")
    classification_llm: str = Field(alias="CLASSIFICATION_LLM")
    question_generation_llm: str = Field(alias="QUESTION_GENERATION_LLM")
    extraction_llm: str = Field(alias="EXTRACTION_LLM")
    answer_generation_llm: str = Field(alias="ANSWER_GENERATION_LLM")
        