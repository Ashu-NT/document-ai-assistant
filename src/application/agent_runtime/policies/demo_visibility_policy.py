from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DemoVisibilityPolicy:
    show_tools: bool = True
    show_observations: bool = True
    show_plan: bool = True
    show_research_plan: bool = True
    show_retrieval_strategy: bool = True
    show_reflection: bool = True
    show_raw_json: bool = False
    show_raw_prompts: bool = False
    show_internal_ids: bool = False
    debug: bool = False
    max_observation_chars: int = 600
    max_step_chars: int = 500
