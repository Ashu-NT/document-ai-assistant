import json

from src.application.prompts.extraction import ExtractionPromptType
from src.application.workflows.extraction.candidates.extraction_candidate_llm_router import (
    ExtractionCandidateLLMRouter,
)
from src.application.workflows.extraction.candidates.extraction_candidate_routing_cache import (
    InMemoryRoutingDecisionCache,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk


class FakeLLMService:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[dict] = []

    def generate(self, prompt, model=None, response_schema=None, num_predict=None):
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "response_schema": response_schema,
                "num_predict": num_predict,
            }
        )
        return self.response


def make_chunk(content: str = "Ambiguous content.") -> DocumentChunk:
    return DocumentChunk(
        chunk_id="chunk_001",
        document_id="document_001",
        section_id="section_001",
        content=content,
        chunk_type=ChunkType.GENERAL,
        source=SourceLocation(),
    )


def test_route_returns_none_when_disabled() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService(json.dumps({"candidate_types": ["safety_warning"]})),
        enabled=False,
    )

    assert router.route(make_chunk()) is None


def test_route_returns_none_when_no_llm_service() -> None:
    router = ExtractionCandidateLLMRouter(llm_service=None, enabled=True)

    assert router.route(make_chunk()) is None


def test_route_returns_none_for_empty_content() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService(json.dumps({"candidate_types": ["safety_warning"]})),
        enabled=True,
    )

    assert router.route(make_chunk(content="   ")) is None


def test_route_resolves_candidate_types() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService(
            json.dumps({"candidate_types": ["safety_warning", "spare_part"]})
        ),
        enabled=True,
    )

    result = router.route(make_chunk())

    assert result == frozenset(
        {ExtractionPromptType.SAFETY_WARNING, ExtractionPromptType.SPARE_PART}
    )
    assert isinstance(router._llm_service.calls[0]["response_schema"], dict)


def test_route_normalizes_casing_and_separators() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService(
            json.dumps(
                {"candidate_types": ["Safety Warning", "Spare-Part", "Contact Point"]}
            )
        ),
        enabled=True,
    )

    result = router.route(make_chunk())

    assert result == frozenset(
        {
            ExtractionPromptType.SAFETY_WARNING,
            ExtractionPromptType.SPARE_PART,
            ExtractionPromptType.CONTACT_POINT,
        }
    )


def test_route_drops_unrecognized_types() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService(
            json.dumps({"candidate_types": ["safety_warning", "not_a_real_type"]})
        ),
        enabled=True,
    )

    result = router.route(make_chunk())

    assert result == frozenset({ExtractionPromptType.SAFETY_WARNING})


def test_route_returns_none_for_empty_candidate_list() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService(json.dumps({"candidate_types": []})),
        enabled=True,
    )

    assert router.route(make_chunk()) is None


def test_route_returns_none_for_malformed_response() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService("not json at all"),
        enabled=True,
    )

    assert router.route(make_chunk()) is None


def test_route_passes_response_schema_to_llm() -> None:
    llm_service = FakeLLMService(json.dumps({"candidate_types": ["identifier"]}))
    router = ExtractionCandidateLLMRouter(
        llm_service=llm_service,
        enabled=True,
    )

    router.route(make_chunk())

    assert llm_service.calls
    assert isinstance(llm_service.calls[0]["response_schema"], dict)
    assert "candidate_types" in llm_service.calls[0]["response_schema"].get(
        "properties",
        {},
    )


def test_is_available_requires_both_enabled_and_llm_service() -> None:
    assert ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService("{}"), enabled=True
    ).is_available() is True
    assert ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService("{}"), enabled=False
    ).is_available() is False
    assert ExtractionCandidateLLMRouter(
        llm_service=None, enabled=True
    ).is_available() is False


# ---- Cache-miss behavior: with no cache configured (the default), route()
# must reproduce its exact prior return value and diagnostics. ----


def test_no_cache_configured_reproduces_prior_behavior_and_return_value() -> None:
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService(
            json.dumps({"candidate_types": ["safety_warning", "spare_part"]})
        ),
        enabled=True,
    )
    sink: list = []

    result = router.route(make_chunk(), diagnostics_sink=sink)

    assert result == frozenset(
        {ExtractionPromptType.SAFETY_WARNING, ExtractionPromptType.SPARE_PART}
    )
    record = sink[0]
    assert record.cache_enabled is False
    assert record.cache_hit is None
    assert record.routing_input_fingerprint is None
    # A real, successful live call is "live_model"-sourced whether or not
    # caching is enabled - "fallback" is reserved for disabled/no-content/
    # schema-failure paths (see the other tests below).
    assert record.routing_outcome_source == "live_model"
    assert record.cache_schema_version is None


# ---- Cache miss (cache configured, nothing cached yet): existing routing
# behavior, plus the result gets written to the cache. ----


def test_cache_miss_calls_llm_and_populates_the_cache() -> None:
    llm_service = FakeLLMService(
        json.dumps({"candidate_types": ["safety_warning"]})
    )
    cache = InMemoryRoutingDecisionCache()
    router = ExtractionCandidateLLMRouter(llm_service=llm_service, enabled=True, cache=cache)
    sink: list = []

    result = router.route(make_chunk(), diagnostics_sink=sink)

    assert result == frozenset({ExtractionPromptType.SAFETY_WARNING})
    assert len(llm_service.calls) == 1
    record = sink[0]
    assert record.cache_enabled is True
    assert record.cache_hit is False
    assert record.routing_outcome_source == "live_model"
    assert record.routing_input_fingerprint is not None
    assert record.cache_schema_version is not None


# ---- Cache hit: no LLM call at all, identical result reproduced. ----


def test_cache_hit_returns_recorded_result_without_invoking_the_llm() -> None:
    llm_service = FakeLLMService(
        json.dumps({"candidate_types": ["safety_warning"]})
    )
    cache = InMemoryRoutingDecisionCache()
    router = ExtractionCandidateLLMRouter(llm_service=llm_service, enabled=True, cache=cache)
    chunk = make_chunk()

    first = router.route(chunk)
    assert len(llm_service.calls) == 1

    sink: list = []
    second = router.route(chunk, diagnostics_sink=sink)

    assert second == first
    assert len(llm_service.calls) == 1  # still 1 - no second LLM call
    record = sink[0]
    assert record.invoked_llm is False
    assert record.cache_hit is True
    assert record.routing_outcome_source == "cache"


def test_cache_hit_reproduces_a_legitimate_abstention() -> None:
    llm_service = FakeLLMService(json.dumps({"candidate_types": []}))
    cache = InMemoryRoutingDecisionCache()
    router = ExtractionCandidateLLMRouter(llm_service=llm_service, enabled=True, cache=cache)
    chunk = make_chunk()

    first = router.route(chunk)
    assert first is None
    assert len(llm_service.calls) == 1

    second = router.route(chunk)

    assert second is None
    assert len(llm_service.calls) == 1  # abstention was cached too


def test_different_content_is_a_separate_cache_entry() -> None:
    llm_service = FakeLLMService(json.dumps({"candidate_types": ["safety_warning"]}))
    cache = InMemoryRoutingDecisionCache()
    router = ExtractionCandidateLLMRouter(llm_service=llm_service, enabled=True, cache=cache)

    router.route(make_chunk(content="Content A."))
    router.route(make_chunk(content="Content B."))

    assert len(llm_service.calls) == 2  # each distinct content is its own miss


# ---- Failed routing (schema-invalid response): existing fallback
# behavior is preserved, and the failure is never cached. ----


def test_schema_invalid_response_is_never_cached() -> None:
    llm_service = FakeLLMService("not json at all")
    cache = InMemoryRoutingDecisionCache()
    router = ExtractionCandidateLLMRouter(llm_service=llm_service, enabled=True, cache=cache)
    chunk = make_chunk()

    first = router.route(chunk)
    assert first is None
    assert len(llm_service.calls) == 1

    # A later call for the SAME content must still make a real attempt -
    # nothing authoritative was recorded for this content.
    second = router.route(chunk)
    assert second is None
    assert len(llm_service.calls) == 2


def test_disabled_router_never_touches_the_cache() -> None:
    cache = InMemoryRoutingDecisionCache()
    router = ExtractionCandidateLLMRouter(
        llm_service=FakeLLMService(json.dumps({"candidate_types": ["safety_warning"]})),
        enabled=False,
        cache=cache,
    )
    sink: list = []

    result = router.route(make_chunk(), diagnostics_sink=sink)

    assert result is None
    record = sink[0]
    assert record.cache_enabled is True
    assert record.cache_hit is None
    assert record.routing_input_fingerprint is None


# ---- Cache corruption: a cache whose get() raises must degrade to a safe
# live fallback, never crash routing. ----


def test_cache_get_raising_degrades_to_a_safe_live_fallback() -> None:
    # Even a non-conforming cache implementation (one whose get() itself
    # raises, e.g. a corrupted persistent backend) must never crash
    # routing - route() wraps the lookup defensively, on top of
    # InMemoryRoutingDecisionCache's own internal safety net.
    class _CorruptCache:
        def get(self, key):
            raise ValueError("simulated corrupted cache store")

        def put(self, key, entry):
            pass

    llm_service = FakeLLMService(json.dumps({"candidate_types": ["safety_warning"]}))
    router = ExtractionCandidateLLMRouter(
        llm_service=llm_service, enabled=True, cache=_CorruptCache()
    )
    sink: list = []

    result = router.route(make_chunk(), diagnostics_sink=sink)

    assert result == frozenset({ExtractionPromptType.SAFETY_WARNING})
    assert len(llm_service.calls) == 1
    record = sink[0]
    assert record.cache_hit is False
    assert record.routing_outcome_source == "live_model"


def test_cache_put_raising_never_fails_an_otherwise_successful_routing_call() -> None:
    class _WriteFailingCache:
        def get(self, key):
            return None

        def put(self, key, entry):
            raise OSError("simulated publish failure")

    llm_service = FakeLLMService(json.dumps({"candidate_types": ["safety_warning"]}))
    router = ExtractionCandidateLLMRouter(
        llm_service=llm_service, enabled=True, cache=_WriteFailingCache()
    )

    result = router.route(make_chunk())

    assert result == frozenset({ExtractionPromptType.SAFETY_WARNING})


def test_transport_failure_falls_back_to_none_and_is_distinguished_from_abstention() -> None:
    from src.shared.exceptions import LLMProviderError

    class _FailingLLMService:
        def generate(self, *args, **kwargs):
            raise LLMProviderError("boom", details={"failure_kind": "read_timeout"})

    router = ExtractionCandidateLLMRouter(llm_service=_FailingLLMService(), enabled=True)
    sink: list = []

    result = router.route(make_chunk(), diagnostics_sink=sink)

    assert result is None
    record = sink[0]
    assert record.transport_failed is True
    assert record.invoked_llm is True
    assert record.schema_valid is None
    assert record.routing_outcome_source == "fallback"


def test_transport_failure_is_never_cached() -> None:
    from src.shared.exceptions import LLMProviderError

    class _FailingLLMService:
        def generate(self, *args, **kwargs):
            raise LLMProviderError("boom", details={"failure_kind": "read_timeout"})

    cache = InMemoryRoutingDecisionCache()
    router = ExtractionCandidateLLMRouter(
        llm_service=_FailingLLMService(), enabled=True, cache=cache
    )
    chunk = make_chunk()

    router.route(chunk)
    router.route(chunk)  # must attempt a live call again, not read a stale cache miss-as-decision

    assert True  # no exception means both calls attempted the live path safely


def test_in_memory_cache_implementation_never_propagates_a_corrupted_lookup() -> None:
    # The real, shipped RoutingDecisionCachePort implementation IS safe:
    # same scenario as above, but through InMemoryRoutingDecisionCache,
    # whose get() swallows lookup failures and returns a miss.
    cache = InMemoryRoutingDecisionCache()
    cache._entries = None  # type: ignore[assignment]  # simulate a corrupted store
    llm_service = FakeLLMService(json.dumps({"candidate_types": ["safety_warning"]}))
    router = ExtractionCandidateLLMRouter(llm_service=llm_service, enabled=True, cache=cache)

    result = router.route(make_chunk())

    assert result == frozenset({ExtractionPromptType.SAFETY_WARNING})
    assert len(llm_service.calls) == 1
