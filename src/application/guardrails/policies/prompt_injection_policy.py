from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from src.config.paths import PROJECT_ROOT
from src.config.yaml_config_loader import load_yaml_config

_CONFIG_PATH = PROJECT_ROOT / "src" / "config" / "guardrails" / "prompt_injection.yaml"


@lru_cache(maxsize=1)
def _config() -> dict:
    return load_yaml_config(
        _CONFIG_PATH, description="Prompt injection guardrail policy"
    )


def _blocked_markers() -> tuple[str, ...]:
    return tuple(_config()["blocked_markers"])


@dataclass(slots=True, frozen=True)
class PromptInjectionPolicy:
    blocked_markers: tuple[str, ...] = field(default_factory=_blocked_markers)
