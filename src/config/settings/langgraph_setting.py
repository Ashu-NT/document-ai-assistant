from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class LangGraphSettings(AppBaseSettings):
    enabled: bool = Field(alias="LANGGRAPH_ENABLED")

    checkpointing: bool = Field(
        alias="LANGGRAPH_CHECKPOINTING"
    )

    max_steps: int = Field(alias="LANGGRAPH_MAX_STEPS")
    llm_planning_enabled: bool = Field(
        default=False,
        alias="LANGGRAPH_LLM_PLANNING_ENABLED"
    )
    reflection_enabled: bool = Field(
        default=False,
        alias="LANGGRAPH_REFLECTION_ENABLED",
    )
    reflection_show: bool = Field(
        default=False,
        alias="LANGGRAPH_SHOW_REFLECTION",
    )
