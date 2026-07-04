from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from src.config.paths import PROJECT_ROOT
from src.config.yaml_config_loader import load_yaml_config

_CONFIG_PATH = PROJECT_ROOT / "src" / "config" / "planning" / "plan_policy.yaml"


@lru_cache(maxsize=1)
def _config() -> dict:
    return load_yaml_config(_CONFIG_PATH, description="Plan policy")


def _allowed_tools() -> set[str]:
    return set(_config()["allowed_tools"])


def _blocked_tools() -> set[str]:
    return set(_config()["blocked_tools"])


def _max_steps() -> int:
    return int(_config()["max_steps"])


def _allow_mutating_tools() -> bool:
    return bool(_config()["allow_mutating_tools"])


def _require_document_scope_for_qa() -> bool:
    return bool(_config()["require_document_scope_for_qa"])


def _allow_corpus_wide_retrieval() -> bool:
    return bool(_config()["allow_corpus_wide_retrieval"])


def _allow_ingestion() -> bool:
    return bool(_config()["allow_ingestion"])


def _allow_delete() -> bool:
    return bool(_config()["allow_delete"])


def _allow_reingestion() -> bool:
    return bool(_config()["allow_reingestion"])


def _max_tool_arg_chars() -> int:
    return int(_config()["max_tool_arg_chars"])


@dataclass(slots=True, frozen=True)
class PlanPolicy:
    allowed_tools: set[str] = field(default_factory=_allowed_tools)
    blocked_tools: set[str] = field(default_factory=_blocked_tools)
    max_steps: int = field(default_factory=_max_steps)
    allow_mutating_tools: bool = field(default_factory=_allow_mutating_tools)
    require_document_scope_for_qa: bool = field(
        default_factory=_require_document_scope_for_qa
    )
    allow_corpus_wide_retrieval: bool = field(
        default_factory=_allow_corpus_wide_retrieval
    )
    allow_ingestion: bool = field(default_factory=_allow_ingestion)
    allow_delete: bool = field(default_factory=_allow_delete)
    allow_reingestion: bool = field(default_factory=_allow_reingestion)
    max_tool_arg_chars: int = field(default_factory=_max_tool_arg_chars)

    @classmethod
    def default(cls) -> "PlanPolicy":
        return cls()
