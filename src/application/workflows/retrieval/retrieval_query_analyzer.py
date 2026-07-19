from src.application.workflows.retrieval.retrieval_query_chunk_type_preference_mapper import (
    RetrievalQueryChunkTypePreferenceMapper,
)
from src.application.workflows.retrieval.retrieval_query_identifier_extractor import (
    RetrievalQueryIdentifierExtractor,
)
from src.application.workflows.retrieval.retrieval_query_intent_inferer import (
    RETRIEVAL_INTENT_RULES_VERSION,
    RetrievalQueryIntentInferer,
)
from src.application.workflows.retrieval.retrieval_query_rewriter import (
    RetrievalQueryRewriter,
)
from src.config.logging import get_logger
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery

_logger = get_logger(__name__)


class RetrievalQueryAnalyzer:
    def __init__(
        self,
        *,
        identifier_extractor: RetrievalQueryIdentifierExtractor | None = None,
        rewriter: RetrievalQueryRewriter | None = None,
        intent_inferer: RetrievalQueryIntentInferer | None = None,
        chunk_type_preference_mapper: (
            RetrievalQueryChunkTypePreferenceMapper | None
        ) = None,
    ) -> None:
        self.identifier_extractor = (
            identifier_extractor or RetrievalQueryIdentifierExtractor()
        )
        self.rewriter = rewriter or RetrievalQueryRewriter()
        self.intent_inferer = intent_inferer or RetrievalQueryIntentInferer()
        self.chunk_type_preference_mapper = (
            chunk_type_preference_mapper
            or RetrievalQueryChunkTypePreferenceMapper()
        )

    def analyze(
        self,
        query: RetrievalQuery,
    ) -> RetrievalQuery:
        identifiers = self._merge_identifiers(
            query.detected_identifiers,
            self.identifier_extractor.extract(query.query_text),
        )
        query.detected_identifiers = identifiers

        rewritten_query = self.rewriter.rewrite(query.query_text)
        if rewritten_query is not None:
            query.rewritten_query = rewritten_query

        classification = self.intent_inferer.classify(query)
        intent = classification.intent
        _logger.info(
            "retrieval_intent_resolved intent=%s query_id=%s rules_version=%s",
            intent.value,
            query.query_id,
            RETRIEVAL_INTENT_RULES_VERSION,
        )
        query.detected_intent = intent.value
        query.intent_best_score = classification.score
        query.intent_runner_up_score = classification.runner_up_score
        query.intent_score_gap = classification.gap
        query.intent_confidence = classification.confidence
        query.intent_runner_up = (
            classification.runner_up_intent.value
            if classification.runner_up_intent is not None
            else None
        )
        preferred_chunk_types = self.chunk_type_preference_mapper.map(
            query=query,
            intent=intent,
        )
        if classification.runner_up_intent is not None and classification.gap == 0:
            # An unresolved scoring tie (see retrieval_query_intent_scorer.py's
            # resolve_scores()): narrowing chunk_types to only the
            # (arbitrarily priority-ranked) winner's list would hard-exclude
            # the tied alternative intent's chunk types from both the dense
            # and SQL candidate pools before scoring ever runs. Widen instead
            # of narrowing when the classification itself is this ambiguous.
            preferred_chunk_types = [
                *preferred_chunk_types,
                *self.chunk_type_preference_mapper.map(
                    query=query,
                    intent=classification.runner_up_intent,
                ),
            ]
        query.chunk_types = self._merge_chunk_types(
            existing=query.chunk_types,
            preferred=preferred_chunk_types,
        )
        query.analyzed = True
        return query

    @staticmethod
    def _merge_identifiers(
        existing: list[str],
        detected: list[str],
    ) -> list[str]:
        merged: list[str] = []
        for value in [*existing, *detected]:
            normalized = (value or "").strip().lower()
            if normalized and normalized not in merged:
                merged.append(normalized)
        return merged

    @staticmethod
    def _merge_chunk_types(
        *,
        existing: list[ChunkType],
        preferred: list[ChunkType],
    ) -> list[ChunkType]:
        ordered: list[ChunkType] = []
        for value in [*existing, *preferred]:
            if value not in ordered:
                ordered.append(value)
        return ordered
