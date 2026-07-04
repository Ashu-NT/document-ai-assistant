from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from src.config.paths import PROJECT_ROOT
from src.config.yaml_config_loader import load_yaml_config

_CONFIG_PATH = PROJECT_ROOT / "src" / "config" / "guardrails" / "domain_scope.yaml"


@lru_cache(maxsize=1)
def _config() -> dict:
    return load_yaml_config(_CONFIG_PATH, description="Domain scope guardrail policy")


def _allowed_scope_signals() -> tuple[str, ...]:
    return tuple(_config()["allowed_scope_signals"])


def _command_signals() -> tuple[str, ...]:
    return tuple(_config()["command_signals"])


def _out_of_scope_signals() -> tuple[str, ...]:
    return tuple(_config()["out_of_scope_signals"])


def _minimum_meaningful_words() -> int:
    return int(_config()["minimum_meaningful_words"])


@dataclass(slots=True, frozen=True)
class DomainScopePolicy:
    allowed_scope_signals: tuple[str, ...] = field(
        default_factory=_allowed_scope_signals
    )
    command_signals: tuple[str, ...] = field(default_factory=_command_signals)
    out_of_scope_signals: tuple[str, ...] = field(
        default_factory=_out_of_scope_signals
    )
    minimum_meaningful_words: int = field(default_factory=_minimum_meaningful_words)
