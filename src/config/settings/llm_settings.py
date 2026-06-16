from pydantic import Field
from pydantic_settings import BaseSettings


class LLMSettings(BaseSettings):
    ollama_base_url: str = Field(alias="OLLAMA_BASE_URL")

    general_llm: str = Field(alias="GENERAL_LLM")
    classification_llm: str = Field(alias="CLASSIFICATION_LLM")
    question_generation_llm: str = Field(alias="QUESTION_GENERATION_LLM")
    extraction_llm: str = Field(alias="EXTRACTION_LLM")

    class Config:
        env_file = ".env"
        extra = "ignore"
        