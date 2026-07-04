from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from src.config.paths import PROJECT_ROOT
from src.config.yaml_config_loader import load_yaml_config

_CONFIG_PATH = PROJECT_ROOT / "src" / "config" / "guardrails" / "unsafe_action.yaml"


@lru_cache(maxsize=1)
def _config() -> dict:
    return load_yaml_config(_CONFIG_PATH, description="Unsafe action guardrail policy")


def _direct_blocked_phrases() -> tuple[str, ...]:
    return tuple(_config()["direct_blocked_phrases"])


def _destructive_verbs() -> tuple[str, ...]:
    return tuple(_config()["destructive_verbs"])


def _mutating_verbs() -> tuple[str, ...]:
    return tuple(_config()["mutating_verbs"])


def _corpus_objects() -> tuple[str, ...]:
    return tuple(_config()["corpus_objects"])


def _mass_modifiers() -> tuple[str, ...]:
    return tuple(_config()["mass_modifiers"])


@dataclass(slots=True, frozen=True)
class UnsafeActionPolicy:
    direct_blocked_phrases: tuple[str, ...] = field(
        default_factory=_direct_blocked_phrases
    )
    destructive_verbs: tuple[str, ...] = field(default_factory=_destructive_verbs)
    mutating_verbs: tuple[str, ...] = field(default_factory=_mutating_verbs)
    corpus_objects: tuple[str, ...] = field(default_factory=_corpus_objects)
    mass_modifiers: tuple[str, ...] = field(default_factory=_mass_modifiers)
