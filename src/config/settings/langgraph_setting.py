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
    deep_research_enabled: bool = Field(
        default=False,
        alias="LANGGRAPH_DEEP_RESEARCH_ENABLED",
    )
    llm_research_planning_enabled: bool = Field(
        default=False,
        alias="LANGGRAPH_LLM_RESEARCH_PLANNING_ENABLED",
    )
    show_research_plan: bool = Field(
        default=False,
        alias="LANGGRAPH_SHOW_RESEARCH_PLAN",
    )
    show_research_trace: bool = Field(
        default=False,
        alias="LANGGRAPH_SHOW_RESEARCH_TRACE",
    )
    reflection_enabled: bool = Field(
        default=False,
        alias="LANGGRAPH_REFLECTION_ENABLED",
    )
    reflection_show: bool = Field(
        default=False,
        alias="LANGGRAPH_SHOW_REFLECTION",
    )
    retrieval_strategy_enabled: bool = Field(
        default=True,
        alias="LANGGRAPH_RETRIEVAL_STRATEGY_ENABLED",
    )
    llm_retrieval_strategy_enabled: bool = Field(
        default=False,
        alias="LANGGRAPH_LLM_RETRIEVAL_STRATEGY_ENABLED",
    )
    show_retrieval_strategy: bool = Field(
        default=False,
        alias="LANGGRAPH_SHOW_RETRIEVAL_STRATEGY",
    )
