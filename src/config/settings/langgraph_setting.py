from pydantic import Field
from pydantic_settings import BaseSettings


class LangGraphSettings(BaseSettings):
    enabled: bool = Field(alias="LANGGRAPH_ENABLED")

    checkpointing: bool = Field(
        alias="LANGGRAPH_CHECKPOINTING"
    )

    max_steps: int = Field(alias="LANGGRAPH_MAX_STEPS")

    class Config:
        env_file = ".env"
        