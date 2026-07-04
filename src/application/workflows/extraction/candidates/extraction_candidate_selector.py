from src.application.prompts.extraction import ExtractionPromptType
from src.application.workflows.extraction.candidates.extraction_candidate_llm_router import (
    ExtractionCandidateLLMRouter,
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
        self, chunk: DocumentChunk
    ) -> frozenset[ExtractionPromptType]:
        cross_signals = self._cross_signal_detector.detect(chunk)

        if chunk.chunk_type in _UNGATED_CHUNK_TYPES:
            router_result = (
                self._llm_router.route(chunk)
                if self._llm_router is not None
                else None
            )
            base = router_result if router_result is not None else _ALL_CANDIDATES
        else:
            base = self.select(chunk.chunk_type)

        return base | _ALWAYS_CANDIDATE | cross_signals

    @staticmethod
    def all_types() -> frozenset[ExtractionPromptType]:
        return _ALL_CANDIDATES
