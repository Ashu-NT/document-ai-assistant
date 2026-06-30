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
_MUTATING_VERBS = ("reingest", "rebuild")
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
_MASS_MODIFIERS = ("all", "every", "existing", "whole", "entire")


@dataclass(slots=True, frozen=True)
class UnsafeActionPolicy:
    direct_blocked_phrases: tuple[str, ...] = field(
        default_factory=lambda: _DIRECT_BLOCKED_PHRASES
    )
    destructive_verbs: tuple[str, ...] = field(
        default_factory=lambda: _DESTRUCTIVE_VERBS
    )
    mutating_verbs: tuple[str, ...] = field(default_factory=lambda: _MUTATING_VERBS)
    corpus_objects: tuple[str, ...] = field(default_factory=lambda: _CORPUS_OBJECTS)
    mass_modifiers: tuple[str, ...] = field(default_factory=lambda: _MASS_MODIFIERS)
