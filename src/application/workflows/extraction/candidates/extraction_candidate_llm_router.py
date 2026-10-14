from src.application.prompts.extraction import ExtractionPromptType
from src.application.prompts.extraction.candidate_router import (
    ExtractionCandidateRouterPromptBuilder,
)
from src.application.workflows.extraction.candidates.extraction_candidate_router_response_parser import (
    ExtractionCandidateRouterResponseParser,
)
from src.application.workflows.extraction.candidates.extraction_candidate_router_schema import (
    build_extraction_candidate_router_json_schema,
)
from src.application.workflows.extraction.candidates.extraction_candidate_routing_cache import (
    ROUTING_CACHE_SCHEMA_VERSION,
    RoutingCacheEntry,
    RoutingDecisionCachePort,
    compute_routing_cache_key,
)
from src.application.workflows.extraction.candidates.extraction_candidate_routing_diagnostics import (
    LLMRoutingInvocationDiagnostics,
    sorted_type_values,
)
from src.domain.document import DocumentChunk
from src.shared.exceptions import SchemaValidationError

# The router's live call never pins a temperature (see route() below), so
# routing is currently subject to whatever sampling temperature the
# provider defaults to. Recorded explicitly (rather than just omitted) in
# every cache key so a future change that starts pinning a real value
# naturally produces a different key, with no separate cache migration
# needed.
_ROUTING_TEMPERATURE: float | None = None


def _default_enabled() -> bool:
    try:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_candidate_router_enabled
    except Exception:
        return False


def _default_model() -> str | None:
    try:
        from src.config.settings import llm_settings

        return llm_settings.extraction_llm or llm_settings.general_llm
    except Exception:
        return None


class ExtractionCandidateLLMRouter:
    """
    Optional LLM fallback for chunks whose ChunkType stayed GENERAL/UNKNOWN
    even after ChunkTypeClassificationWorkflow's own LLM fallback. Instead
    of ExtractionCandidateSelector failing open to "ask about every entity
    type" for such chunks, this makes one targeted call asking the LLM
    directly which entity types are worth extracting from this specific
    chunk.

    Disabled by default (EXTRACTION_CANDIDATE_ROUTER_ENABLED=false): this
    adds an LLM call for every otherwise-unresolved chunk, which works
    against "don't spin up the LLM for irrelevant chunks" unless the
    narrower downstream prompts it enables save more than this call costs.
    """

    def __init__(
        self,
        *,
        llm_service=None,
        model: str | None = None,
        enabled: bool | None = None,
        prompt_builder: ExtractionCandidateRouterPromptBuilder | None = None,
        cache: RoutingDecisionCachePort | None = None,
    ) -> None:
        self._llm_service = llm_service
        self._model = model or _default_model()
        self._enabled = enabled if enabled is not None else _default_enabled()
        self._prompt_builder = prompt_builder or ExtractionCandidateRouterPromptBuilder()
        self._response_parser = ExtractionCandidateRouterResponseParser()
        # Optional, versioned routing-decision cache. `None` (the default)
        # reproduces this class's exact prior behavior: every eligible
        # chunk always makes a live call, nothing is ever cached or looked
        # up. See extraction_candidate_routing_cache.py.
        self._cache = cache

    def is_available(self) -> bool:
        return self._enabled and self._llm_service is not None

    def route(
        self,
        chunk: DocumentChunk,
        *,
        diagnostics_sink: list[LLMRoutingInvocationDiagnostics] | None = None,
    ) -> frozenset[ExtractionPromptType] | None:
        available = self.is_available()
        had_content = bool(chunk.content and chunk.content.strip())
        cache_enabled = self._cache is not None
        if not available or not had_content:
            self._record(
                diagnostics_sink,
                available=available,
                had_content=had_content,
                invoked_llm=False,
                schema_valid=None,
                resolved_types=None,
                cache_enabled=cache_enabled,
            )
            return None

        routing_key = (
            compute_routing_cache_key(
                chunk.content, model=self._model or "", temperature=_ROUTING_TEMPERATURE
            )
            if self._cache is not None
            else None
        )

        if routing_key is not None:
            try:
                cached_entry = self._cache.get(routing_key)
            except Exception:  # noqa: BLE001 - a non-conforming/corrupted
                # cache implementation must degrade this one lookup to a
                # safe miss (fall through to a live call), never crash
                # routing - this is on top of, not instead of,
                # InMemoryRoutingDecisionCache's own internal safety.
                cached_entry = None
            if cached_entry is not None:
                result = (
                    frozenset(
                        ExtractionPromptType(value) for value in cached_entry.resolved_types
                    )
                    if cached_entry.resolved_types
                    else None
                )
                self._record(
                    diagnostics_sink,
                    available=True,
                    had_content=True,
                    invoked_llm=False,
                    schema_valid=True,
                    resolved_types=cached_entry.resolved_types,
                    cache_enabled=True,
                    cache_hit=True,
                    routing_input_fingerprint=routing_key.cache_key,
                    routing_outcome_source="cache",
                    cache_schema_version=cached_entry.schema_version,
                )
                return result

        prompt = self._prompt_builder.build(chunk.content)
        response = self._llm_service.generate(
            prompt,
            model=self._model,
            response_schema=build_extraction_candidate_router_json_schema(),
        )
        try:
            payload = self._response_parser.parse(response)
        except SchemaValidationError:
            # A schema-invalid response is a transient/operational failure
            # of this one call, not an authoritative decision about this
            # content - it must never be written to the cache (a retry, or
            # a later call for the same content, must still get a real
            # live attempt).
            self._record(
                diagnostics_sink,
                available=True,
                had_content=True,
                invoked_llm=True,
                schema_valid=False,
                resolved_types=None,
                cache_enabled=cache_enabled,
                cache_hit=False if routing_key is not None else None,
                routing_input_fingerprint=(
                    routing_key.cache_key if routing_key is not None else None
                ),
                routing_outcome_source="fallback",
            )
            return None

        resolved = payload.resolved_types()
        result = resolved or None
        resolved_type_values = sorted_type_values(result) if result else None

        if routing_key is not None:
            # Both a real decision AND a legitimate abstention (empty
            # candidate list) are genuine, successful, repeatable outcomes
            # - both get cached. Only a failed/unavailable call (handled
            # above/earlier) is never written here. A publish failure must
            # never turn an already-successful routing decision into a
            # crash - the decision is still returned below either way.
            try:
                self._cache.put(
                    routing_key,
                    RoutingCacheEntry(
                        resolved_types=resolved_type_values,
                        schema_version=ROUTING_CACHE_SCHEMA_VERSION,
                    ),
                )
            except Exception:  # noqa: BLE001 - see try/except around .get() above
                pass

        self._record(
            diagnostics_sink,
            available=True,
            had_content=True,
            invoked_llm=True,
            schema_valid=True,
            resolved_types=resolved_type_values,
            cache_enabled=cache_enabled,
            cache_hit=False if routing_key is not None else None,
            routing_input_fingerprint=(
                routing_key.cache_key if routing_key is not None else None
            ),
            routing_outcome_source="live_model",
            cache_schema_version=ROUTING_CACHE_SCHEMA_VERSION if routing_key is not None else None,
        )
        return result

    @staticmethod
    def _record(
        diagnostics_sink: list[LLMRoutingInvocationDiagnostics] | None,
        **fields: object,
    ) -> None:
        if diagnostics_sink is None:
            return
        diagnostics_sink.append(LLMRoutingInvocationDiagnostics(**fields))
