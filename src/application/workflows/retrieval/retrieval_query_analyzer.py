from src.application.workflows.retrieval.retrieval_query_chunk_type_preference_mapper import (
    RetrievalQueryChunkTypePreferenceMapper,
)
from src.application.workflows.retrieval.retrieval_query_identifier_extractor import (
    RetrievalQueryIdentifierExtractor,
)
from src.application.workflows.retrieval.retrieval_query_intent_inferer import (
    RetrievalQueryIntentInferer,
)
from src.application.workflows.retrieval.retrieval_query_rewriter import (
    RetrievalQueryRewriter,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery


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

        intent = self.intent_inferer.infer(query)
        preferred_chunk_types = self.chunk_type_preference_mapper.map(
            query=query,
            intent=intent,
        )
        query.chunk_types = self._merge_chunk_types(
            existing=query.chunk_types,
            preferred=preferred_chunk_types,
        )
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
