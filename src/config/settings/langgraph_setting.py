from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class LangGraphSettings(AppBaseSettings):
    enabled: bool = Field(alias="LANGGRAPH_ENABLED")

    checkpointing: bool = Field(
        alias="LANGGRAPH_CHECKPOINTING"
    )

    max_steps: int = Field(alias="LANGGRAPH_MAX_STEPS")
        