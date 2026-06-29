from __future__ import annotations

from dataclasses import dataclass, field

_DIRECT_BLOCKED_PHRASES = (
    "delete all documents",
    "delete every document",
    "remove all documents",
    "wipe corpus",
    "clear corpus",
    "drop corpus",
    "delete vectors",
    "delete existing vectors",
    "clear qdrant",
    "wipe qdrant",
    "remove all chunks",
    "delete all chunks",
    "reingest every document",
    "reingest all documents",
    "rebuild whole corpus",
    "delete and reingest",
    "drop database",
    "wipe database",
    "reset database",
    "truncate tables",
)
_DESTRUCTIVE_VERBS = (
    "delete",
    "remove",
    "wipe",
    "clear",
    "drop",
    "reset",
    "truncate",
    "purge",
)
_MUTATING_VERBS = (
    "reingest",
    "rebuild",
)
_CORPUS_OBJECTS = (
    "document corpus",
    "corpus",
    "documents",
    "document",
    "vectors",
    "vector",
    "qdrant",
    "chunks",
    "chunk",
    "database",
    "db",
    "tables",
    "table",
)
_MASS_MODIFIERS = (
    "all",
    "every",
    "existing",
    "whole",
    "entire",
)


@dataclass(frozen=True, slots=True)
class UnsafeActionDecision:
    is_unsafe: bool
    reason: str | None = None
    matched_terms: list[str] = field(default_factory=list)
    severity: str = "blocked"


class UnsafeActionDetector:
    def detect(self, user_input: str) -> UnsafeActionDecision:
        normalized = " ".join(user_input.strip().lower().split())
        if not normalized:
            return UnsafeActionDecision(is_unsafe=False)

        direct_matches = [
            phrase for phrase in _DIRECT_BLOCKED_PHRASES if phrase in normalized
        ]
        if direct_matches:
            return UnsafeActionDecision(
                is_unsafe=True,
                reason="Request attempts destructive corpus mutation.",
                matched_terms=direct_matches,
            )

        matched_terms: list[str] = []
        destructive_verb = _first_present(normalized, _DESTRUCTIVE_VERBS)
        mutating_verb = _first_present(normalized, _MUTATING_VERBS)
        corpus_object = _first_present(normalized, _CORPUS_OBJECTS)
        mass_modifier = _first_present(normalized, _MASS_MODIFIERS)

        if destructive_verb and corpus_object:
            matched_terms.extend([destructive_verb, corpus_object])
            if mass_modifier:
                matched_terms.append(mass_modifier)
            return UnsafeActionDecision(
                is_unsafe=True,
                reason="Request combines destructive action with corpus storage objects.",
                matched_terms=_dedupe_preserving_order(matched_terms),
            )

        if mutating_verb and corpus_object:
            matched_terms.extend([mutating_verb, corpus_object])
            if mass_modifier:
                matched_terms.append(mass_modifier)
            return UnsafeActionDecision(
                is_unsafe=True,
                reason="Request attempts whole-corpus reingestion or rebuild.",
                matched_terms=_dedupe_preserving_order(matched_terms),
            )

        return UnsafeActionDecision(is_unsafe=False)


def _first_present(value: str, candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if candidate in value:
            return candidate
    return None


def _dedupe_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
