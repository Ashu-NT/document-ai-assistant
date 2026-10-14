from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol

# Bump whenever the routing prompt template, the routing response schema,
# or the set of inputs that feed a routing decision changes in a way that
# could change what a previously-cached decision means. Bumping this
# changes every entry's cache_key, so stale entries are simply never
# looked up again (they are not migrated or deleted) - mirrors
# PARSED_ARTIFACT_SCHEMA_VERSION's exact precedent (see
# src/application/workflows/parsing/artifact_store/parsed_artifact_key.py).
ROUTING_CACHE_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class RoutingCacheKey:
    """Identity of a cacheable candidate-routing decision.

    Two routing calls land on the same cache entry iff every field here is
    equal: same chunk content, same model, same temperature (recorded
    explicitly, even when `None` - the router's live call does not
    currently pin a temperature, so routing is implicitly subject to
    whatever the provider's own default sampling is; recording `None`
    here rather than omitting it means a future change that starts
    pinning a real temperature value naturally produces a different key,
    with no separate migration needed), and the same cache schema
    version.
    """

    content_sha256: str
    model: str
    temperature: float | None
    schema_version: int = ROUTING_CACHE_SCHEMA_VERSION

    @property
    def cache_key(self) -> str:
        canonical = "|".join(
            [
                str(self.schema_version),
                self.content_sha256,
                self.model,
                "" if self.temperature is None else repr(self.temperature),
            ]
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compute_routing_cache_key(
    content: str, *, model: str, temperature: float | None
) -> RoutingCacheKey:
    content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return RoutingCacheKey(
        content_sha256=content_sha256, model=model, temperature=temperature
    )


@dataclass(frozen=True, slots=True)
class RoutingCacheEntry:
    """A previously-recorded, successful (schema-valid) routing outcome.

    `resolved_types` is `None` for a legitimate abstention - the router ran
    and the model explicitly returned no candidate types - which is
    distinct from "no entry exists" (never asked, or asked and the call
    itself was unavailable / returned a malformed response). Only a
    genuinely successful, schema-valid response ever reaches `put()`; see
    `ExtractionCandidateLLMRouter.route()`.
    """

    resolved_types: tuple[str, ...] | None
    schema_version: int


class RoutingDecisionCachePort(Protocol):
    def get(self, key: RoutingCacheKey) -> RoutingCacheEntry | None: ...

    def put(self, key: RoutingCacheKey, entry: RoutingCacheEntry) -> None: ...


class InMemoryRoutingDecisionCache:
    """Reference `RoutingDecisionCachePort` implementation: a plain
    in-process dict, scoped to this process/instance only (no persistence,
    no cross-process sharing - exactly what "optional" caching needs for a
    single evaluation run or a single long-lived service process).

    `get()` never raises and never returns a stale-schema entry: any
    lookup failure, or an entry whose `schema_version` no longer matches
    the key's, is treated as a safe cache miss rather than a crash or a
    silently-wrong decision. This is the "cache corruption -> safe
    fallback" contract a future persistent backend (file/DB) must also
    honor.
    """

    def __init__(self) -> None:
        self._entries: dict[str, RoutingCacheEntry] = {}

    def get(self, key: RoutingCacheKey) -> RoutingCacheEntry | None:
        try:
            entry = self._entries.get(key.cache_key)
        except Exception:  # noqa: BLE001 - any lookup failure is a safe miss
            return None
        if entry is None:
            return None
        if entry.schema_version != key.schema_version:
            return None
        return entry

    def put(self, key: RoutingCacheKey, entry: RoutingCacheEntry) -> None:
        self._entries[key.cache_key] = entry
