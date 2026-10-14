from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class LLMRoutingInvocationDiagnostics:
    """Ground-truth record of one `ExtractionCandidateLLMRouter.route()`
    call. `route()` itself collapses "router disabled", "empty chunk
    content", and "schema validation failed" to the same `None` return
    value -- correct for production behavior, but not enough to diagnose
    WHY a chunk's candidates came out the way they did. This record keeps
    those cases distinguishable without changing what `route()` returns.
    """

    available: bool
    had_content: bool
    invoked_llm: bool
    schema_valid: bool | None
    resolved_types: tuple[str, ...] | None
    # Routing-decision-cache diagnostics. All default so every existing construction site
    # (and every existing test) keeps working unchanged when a cache isn't
    # configured at all.
    cache_enabled: bool = False
    cache_hit: bool | None = None
    routing_input_fingerprint: str | None = None
    routing_outcome_source: str = "fallback"
    cache_schema_version: int | None = None
    transport_failed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "available": self.available,
            "had_content": self.had_content,
            "invoked_llm": self.invoked_llm,
            "schema_valid": self.schema_valid,
            "resolved_types": (
                list(self.resolved_types) if self.resolved_types is not None else None
            ),
            "cache_enabled": self.cache_enabled,
            "cache_hit": self.cache_hit,
            "routing_input_fingerprint": self.routing_input_fingerprint,
            "routing_outcome_source": self.routing_outcome_source,
            "transport_failed": self.transport_failed,
            "cache_schema_version": self.cache_schema_version,
        }


@dataclass(slots=True, frozen=True)
class ExtractionCandidateRoutingDiagnostics:
    """One per-chunk record of how `ExtractionCandidateSelector.select_for_chunk`
    arrived at its final requested entity-type set.

    Purely observational: appending this record never changes
    `select_for_chunk`'s return value, the rendered prompt, or any
    extraction output -- see
    `test_extraction_candidate_routing_diagnostics_do_not_alter_behavior.py`
    for the equivalence proof. All type lists are stored as tuples sorted
    by their string value so repeated runs produce byte-identical,
    diffable records regardless of any hash-randomization-driven set
    iteration order upstream.
    """

    document_id: str | None
    batch_index: int | None
    batch_count: int | None
    chunk_id: str
    chunk_type: str
    is_ungated: bool
    deterministic_candidate_types: tuple[str, ...]
    llm_routing: LLMRoutingInvocationDiagnostics | None
    cross_signal_types: tuple[str, ...]
    always_candidate_types: tuple[str, ...]
    requested_types: tuple[str, ...]
    inclusion_reasons: tuple[tuple[str, tuple[str, ...]], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "document_id": self.document_id,
            "batch_index": self.batch_index,
            "batch_count": self.batch_count,
            "chunk_id": self.chunk_id,
            "chunk_type": self.chunk_type,
            "is_ungated": self.is_ungated,
            "deterministic_candidate_types": list(self.deterministic_candidate_types),
            "llm_routing": self.llm_routing.to_dict() if self.llm_routing else None,
            "cross_signal_types": list(self.cross_signal_types),
            "always_candidate_types": list(self.always_candidate_types),
            "requested_types": list(self.requested_types),
            "inclusion_reasons": {
                type_value: list(reasons)
                for type_value, reasons in self.inclusion_reasons
            },
        }


def sorted_type_values(types) -> tuple[str, ...]:
    return tuple(sorted(t.value for t in types))
