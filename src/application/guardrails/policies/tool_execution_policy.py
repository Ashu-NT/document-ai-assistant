from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from src.config.paths import PROJECT_ROOT
from src.config.yaml_config_loader import load_yaml_config

_CONFIG_PATH = PROJECT_ROOT / "src" / "config" / "guardrails" / "tool_execution.yaml"


@lru_cache(maxsize=1)
def _config() -> dict:
    return load_yaml_config(_CONFIG_PATH, description="Tool execution guardrail policy")


def _allowed_tools() -> tuple[str, ...]:
    return tuple(_config()["allowed_tools"])


def _blocked_tools() -> tuple[str, ...]:
    return tuple(_config()["blocked_tools"])


def _block_mutating_tools_in_demo() -> bool:
    return bool(_config()["block_mutating_tools_in_demo"])


def _require_registered_tools() -> bool:
    return bool(_config()["require_registered_tools"])


@dataclass(slots=True, frozen=True)
class ToolExecutionPolicy:
    allowed_tools: tuple[str, ...] = field(default_factory=_allowed_tools)
    blocked_tools: tuple[str, ...] = field(default_factory=_blocked_tools)
    block_mutating_tools_in_demo: bool = field(
        default_factory=_block_mutating_tools_in_demo
    )
    require_registered_tools: bool = field(
        default_factory=_require_registered_tools
    )
