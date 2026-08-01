from __future__ import annotations

from dataclasses import dataclass, field


def _default_show_research_plan() -> bool:
    try:
        from src.config.settings import langgraph_settings
        return langgraph_settings.show_research_plan
    except Exception:
        return True


def _default_show_retrieval_strategy() -> bool:
    try:
        from src.config.settings import langgraph_settings
        return langgraph_settings.show_retrieval_strategy
    except Exception:
        return True


def _default_show_reflection() -> bool:
    try:
        from src.config.settings import langgraph_settings
        return langgraph_settings.reflection_show
    except Exception:
        return True


@dataclass(slots=True)
class DemoVisibilityPolicy:
    show_tools: bool = True
    show_observations: bool = True
    show_plan: bool = True
    show_research_plan: bool = field(default_factory=_default_show_research_plan)
    show_retrieval_strategy: bool = field(default_factory=_default_show_retrieval_strategy)
    show_reflection: bool = field(default_factory=_default_show_reflection)
    show_raw_evidence: bool = False
    show_raw_json: bool = False
    show_raw_prompts: bool = False
    show_internal_ids: bool = False
    debug: bool = False
    max_observation_chars: int = 600
    max_step_chars: int = 500
