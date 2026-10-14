from src.application.workflows.extraction.candidates.extraction_candidate_routing_cache import (
    ROUTING_CACHE_SCHEMA_VERSION,
    InMemoryRoutingDecisionCache,
    RoutingCacheEntry,
    RoutingCacheKey,
    compute_routing_cache_key,
)


class TestRoutingCacheKey:
    def test_identical_effective_input_produces_identical_key(self) -> None:
        key_a = compute_routing_cache_key(
            "Danger: hazard present.", model="qwen2.5:7b", temperature=None
        )
        key_b = compute_routing_cache_key(
            "Danger: hazard present.", model="qwen2.5:7b", temperature=None
        )

        assert key_a.cache_key == key_b.cache_key

    def test_changed_content_produces_a_different_key(self) -> None:
        key_a = compute_routing_cache_key(
            "Danger: hazard present.", model="qwen2.5:7b", temperature=None
        )
        key_b = compute_routing_cache_key(
            "Caution advised near moving parts.", model="qwen2.5:7b", temperature=None
        )

        assert key_a.cache_key != key_b.cache_key

    def test_changed_model_produces_a_different_key(self) -> None:
        key_a = compute_routing_cache_key(
            "Danger: hazard present.", model="qwen2.5:7b", temperature=None
        )
        key_b = compute_routing_cache_key(
            "Danger: hazard present.", model="qwen2.5:3b", temperature=None
        )

        assert key_a.cache_key != key_b.cache_key

    def test_changed_temperature_produces_a_different_key(self) -> None:
        key_a = compute_routing_cache_key(
            "Danger: hazard present.", model="qwen2.5:7b", temperature=None
        )
        key_b = compute_routing_cache_key(
            "Danger: hazard present.", model="qwen2.5:7b", temperature=0.0
        )

        assert key_a.cache_key != key_b.cache_key

    def test_changed_schema_version_produces_a_different_key(self) -> None:
        # Simulates "changed routing prompt/schema version": a real code
        # change would bump ROUTING_CACHE_SCHEMA_VERSION itself, which this
        # constructs directly to prove the effect without editing the
        # module constant from a test.
        key_a = RoutingCacheKey(
            content_sha256="abc", model="qwen2.5:7b", temperature=None, schema_version=1
        )
        key_b = RoutingCacheKey(
            content_sha256="abc", model="qwen2.5:7b", temperature=None, schema_version=2
        )

        assert key_a.cache_key != key_b.cache_key

    def test_default_schema_version_matches_module_constant(self) -> None:
        key = compute_routing_cache_key("x", model="m", temperature=None)
        assert key.schema_version == ROUTING_CACHE_SCHEMA_VERSION


class TestInMemoryRoutingDecisionCache:
    def test_put_then_get_round_trips(self) -> None:
        cache = InMemoryRoutingDecisionCache()
        key = compute_routing_cache_key("x", model="m", temperature=None)
        entry = RoutingCacheEntry(
            resolved_types=("safety_warning", "spare_part"),
            schema_version=ROUTING_CACHE_SCHEMA_VERSION,
        )

        cache.put(key, entry)

        assert cache.get(key) == entry

    def test_get_returns_none_when_nothing_published(self) -> None:
        cache = InMemoryRoutingDecisionCache()
        key = compute_routing_cache_key("x", model="m", temperature=None)

        assert cache.get(key) is None

    def test_get_treats_stale_schema_version_as_a_safe_miss(self) -> None:
        cache = InMemoryRoutingDecisionCache()
        key_v1 = RoutingCacheKey(content_sha256="abc", model="m", temperature=None, schema_version=1)
        cache.put(
            key_v1,
            RoutingCacheEntry(resolved_types=("safety_warning",), schema_version=1),
        )

        # Same content/model/temperature, but the *current* schema version
        # has moved on - this must never surface the old, possibly
        # semantically-invalid decision.
        key_v2 = RoutingCacheKey(content_sha256="abc", model="m", temperature=None, schema_version=2)

        assert cache.get(key_v2) is None

    def test_get_never_raises_on_a_corrupted_backing_store(self) -> None:
        class _CorruptDict(dict):
            def get(self, *_args, **_kwargs):
                raise ValueError("simulated corrupted cache store")

        cache = InMemoryRoutingDecisionCache()
        cache._entries = _CorruptDict()  # simulate a corrupted backend
        key = compute_routing_cache_key("x", model="m", temperature=None)

        # Must degrade to a safe miss, never propagate the exception.
        assert cache.get(key) is None

    def test_abstention_entry_with_none_resolved_types_round_trips(self) -> None:
        cache = InMemoryRoutingDecisionCache()
        key = compute_routing_cache_key("x", model="m", temperature=None)
        entry = RoutingCacheEntry(resolved_types=None, schema_version=ROUTING_CACHE_SCHEMA_VERSION)

        cache.put(key, entry)

        retrieved = cache.get(key)
        assert retrieved is not None
        assert retrieved.resolved_types is None
