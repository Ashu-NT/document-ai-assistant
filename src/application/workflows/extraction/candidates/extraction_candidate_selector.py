from src.application.prompts.extraction import ExtractionPromptType
from src.application.workflows.extraction.candidates.extraction_candidate_llm_router import (
    ExtractionCandidateLLMRouter,
)
from src.application.workflows.extraction.candidates.extraction_candidate_routing_diagnostics import (
    ExtractionCandidateRoutingDiagnostics,
    LLMRoutingInvocationDiagnostics,
    sorted_type_values,
)
from src.application.workflows.extraction.candidates.extraction_cross_signal_detector import (
    ExtractionCrossSignalDetector,
)
from src.domain.common import ChunkType
from src.domain.document import DocumentChunk

_ALWAYS_CANDIDATE: frozenset[ExtractionPromptType] = frozenset(
    {ExtractionPromptType.IDENTIFIER}
)
_ALL_CANDIDATES: frozenset[ExtractionPromptType] = frozenset(ExtractionPromptType)

# ChunkType is a single-winner classification (deterministic
# ChunkSemanticSignalExtractor, with an optional LLM fallback for
# GENERAL/UNKNOWN chunks via ChunkTypeClassificationWorkflow) computed
# during parsing/chunking. These two values mean the deterministic signal
# was inconclusive for the chunk, so selection is not narrowed at all.
_UNGATED_CHUNK_TYPES: frozenset[ChunkType] = frozenset(
    {ChunkType.GENERAL, ChunkType.UNKNOWN}
)

# Every other ChunkType member MUST have a deliberate entry here (enforced
# by a completeness test) — an empty frozenset is a deliberate "identifiers
# only" decision (e.g. CERTIFICATION_INFO, DRAWING_REFERENCE), not an
# oversight. An unmapped ChunkType is treated as ungated (fails open to
# _ALL_CANDIDATES) since a missing mapping is a gap in this selector, not a
# signal that nothing is extractable from the chunk.
_CHUNK_TYPE_CANDIDATES: dict[ChunkType, frozenset[ExtractionPromptType]] = {
    ChunkType.OVERVIEW: frozenset(
        {
            ExtractionPromptType.EQUIPMENT,
            ExtractionPromptType.MANUFACTURER,
            ExtractionPromptType.SUPPLIER,
            ExtractionPromptType.CONTACT_POINT,
        }
    ),
    ChunkType.MAINTENANCE_PROCEDURE: frozenset(
        {
            ExtractionPromptType.PROCEDURE,
            ExtractionPromptType.MAINTENANCE_TASK,
        }
    ),
    ChunkType.MAINTENANCE_INTERVAL: frozenset(
        {
            ExtractionPromptType.MAINTENANCE_TASK,
            ExtractionPromptType.MAINTENANCE_INTERVAL,
        }
    ),
    ChunkType.SPARE_PARTS_TABLE: frozenset(
        {
            ExtractionPromptType.SPARE_PART,
            ExtractionPromptType.MANUFACTURER,
            ExtractionPromptType.SUPPLIER,
            ExtractionPromptType.EQUIPMENT,
        }
    ),
    ChunkType.SAFETY_WARNING: frozenset({ExtractionPromptType.SAFETY_WARNING}),
    ChunkType.TROUBLESHOOTING: frozenset(
        {
            ExtractionPromptType.TROUBLESHOOTING,
            ExtractionPromptType.PROCEDURE,
        }
    ),
    ChunkType.TECHNICAL_SPECIFICATION: frozenset(
        {ExtractionPromptType.SPECIFICATION}
    ),
    ChunkType.INSTALLATION_INSTRUCTION: frozenset({ExtractionPromptType.PROCEDURE}),
    ChunkType.OPERATION_INSTRUCTION: frozenset(
        {
            ExtractionPromptType.PROCEDURE,
            ExtractionPromptType.MAINTENANCE_TASK,
        }
    ),
    # Certification/drawing chunks are mostly about the identifier itself
    # (certificate_number / drawing_number) — no other entity type is
    # expected to reliably appear here.
    ChunkType.CERTIFICATION_INFO: frozenset(),
    ChunkType.DRAWING_REFERENCE: frozenset(),
    # Formula/code chunks are unlikely to contain extractable structured
    # entities beyond an identifier that happens to appear nearby.
    ChunkType.FORMULA: frozenset(),
    ChunkType.CODE_BLOCK: frozenset(),
    # Form chunks are raw field/value pairs -- any structured entity worth
    # extracting from them is already captured as an identifier.
    ChunkType.FORM_DATA: frozenset(),
}


class ExtractionCandidateSelector:
    """
    Decides which semantic entity types are worth asking the LLM to
    extract from a chunk, so extraction prompts can eventually be narrowed
    instead of always requesting all entity types from every chunk. Not
    yet wired into ExtractionWorkflow/prompt building — this is a
    standalone, tested decision component pending that follow-up.

        final_candidates = chunk_type_candidates
                            | always_candidates
                            | detected_cross_signals

    - chunk_type_candidates: the chunk's ChunkType mapped through
      _CHUNK_TYPE_CANDIDATES. For chunks still GENERAL/UNKNOWN (the
      deterministic signal was inconclusive), an optional LLM router
      (ExtractionCandidateLLMRouter, disabled by default) substitutes for
      this term; if the router is absent/disabled/inconclusive, this term
      fails open to every entity type rather than narrowing blind.
    - always_candidates: identifiers, exempt from gating — part/serial/
      drawing/certificate numbers appear incidentally in almost any chunk
      type, not concentrated the way e.g. safety-warning language is.
    - detected_cross_signals: ExtractionCrossSignalDetector's deterministic
      keyword/header/regex/table scan of the chunk's own content, catching
      entity types the single-winner ChunkType wouldn't surface (e.g. a
      maintenance-interval table that also names a manufacturer).
    """

    def __init__(
        self,
        *,
        cross_signal_detector: ExtractionCrossSignalDetector | None = None,
        llm_router: ExtractionCandidateLLMRouter | None = None,
    ) -> None:
        self._cross_signal_detector = (
            cross_signal_detector or ExtractionCrossSignalDetector()
        )
        self._llm_router = llm_router

    def select(self, chunk_type: ChunkType) -> frozenset[ExtractionPromptType]:
        if chunk_type in _UNGATED_CHUNK_TYPES:
            return _ALL_CANDIDATES

        if chunk_type not in _CHUNK_TYPE_CANDIDATES:
            return _ALL_CANDIDATES

        return _CHUNK_TYPE_CANDIDATES[chunk_type] | _ALWAYS_CANDIDATE

    def select_for_chunk(
        self,
        chunk: DocumentChunk,
        *,
        diagnostics_sink: list[ExtractionCandidateRoutingDiagnostics] | None = None,
        document_id: str | None = None,
        batch_index: int | None = None,
        batch_count: int | None = None,
    ) -> frozenset[ExtractionPromptType]:
        cross_signals = self._cross_signal_detector.detect(chunk)
        is_ungated = chunk.chunk_type in _UNGATED_CHUNK_TYPES

        llm_routing_diag: LLMRoutingInvocationDiagnostics | None = None
        if is_ungated:
            deterministic_candidates: frozenset[ExtractionPromptType] = frozenset()
            router_diag_sink: list[LLMRoutingInvocationDiagnostics] = []
            router_result = (
                self._llm_router.route(chunk, diagnostics_sink=router_diag_sink)
                if self._llm_router is not None
                else None
            )
            llm_routing_diag = router_diag_sink[0] if router_diag_sink else None
            base = router_result if router_result is not None else _ALL_CANDIDATES
        else:
            deterministic_candidates = _CHUNK_TYPE_CANDIDATES.get(
                chunk.chunk_type, _ALL_CANDIDATES
            )
            base = self.select(chunk.chunk_type)

        final = base | _ALWAYS_CANDIDATE | cross_signals

        if diagnostics_sink is not None:
            diagnostics_sink.append(
                self._build_diagnostics(
                    chunk=chunk,
                    document_id=document_id,
                    batch_index=batch_index,
                    batch_count=batch_count,
                    is_ungated=is_ungated,
                    deterministic_candidates=deterministic_candidates,
                    llm_routing_diag=llm_routing_diag,
                    cross_signals=cross_signals,
                    final=final,
                )
            )

        return final

    @staticmethod
    def _build_diagnostics(
        *,
        chunk: DocumentChunk,
        document_id: str | None,
        batch_index: int | None,
        batch_count: int | None,
        is_ungated: bool,
        deterministic_candidates: frozenset[ExtractionPromptType],
        llm_routing_diag: LLMRoutingInvocationDiagnostics | None,
        cross_signals: frozenset[ExtractionPromptType],
        final: frozenset[ExtractionPromptType],
    ) -> ExtractionCandidateRoutingDiagnostics:
        router_types = (
            frozenset(llm_routing_diag.resolved_types)
            if llm_routing_diag is not None and llm_routing_diag.resolved_types
            else frozenset()
        )
        reasons: dict[str, set[str]] = {}
        for prompt_type in _ALL_CANDIDATES:
            sources: set[str] = set()
            if prompt_type in deterministic_candidates:
                sources.add("deterministic")
            if prompt_type.value in router_types:
                sources.add("llm_router")
            if prompt_type in _ALWAYS_CANDIDATE:
                sources.add("always")
            if prompt_type in cross_signals:
                sources.add("cross_signal")
            reasons[prompt_type.value] = sources

        return ExtractionCandidateRoutingDiagnostics(
            document_id=document_id,
            batch_index=batch_index,
            batch_count=batch_count,
            chunk_id=chunk.chunk_id,
            chunk_type=chunk.chunk_type.value,
            is_ungated=is_ungated,
            deterministic_candidate_types=sorted_type_values(deterministic_candidates),
            llm_routing=llm_routing_diag,
            cross_signal_types=sorted_type_values(cross_signals),
            always_candidate_types=sorted_type_values(_ALWAYS_CANDIDATE),
            requested_types=sorted_type_values(final),
            inclusion_reasons=tuple(
                (type_value, tuple(sorted(sources)))
                for type_value, sources in sorted(reasons.items())
            ),
        )

    @staticmethod
    def all_types() -> frozenset[ExtractionPromptType]:
        return _ALL_CANDIDATES
