from src.application.contracts.retrieval import Reranker
from src.application.workflows.retrieval import RetrievalQueryIntent
from src.application.workflows.retrieval import RetrievalQueryIntentInferer
from src.application.workflows.retrieval.deduplication.retrieved_chunk_signature import (
    detect_chunk_role,
)
from src.domain.retrieval import RetrievalQuery, RetrievedChunk
from src.infrastructure.retrieval.keyword.sql_keyword_query_terms import extract_query_terms
from src.infrastructure.retrieval.rerankers.deterministic.chunk_role_scorer import role_score
from src.infrastructure.retrieval.rerankers.deterministic.intent_chunk_type_scorer import (
    intent_chunk_type_score,
)
from src.infrastructure.retrieval.rerankers.deterministic.reranker_metadata_extractors import (
    identifier_match_count,
    metadata_float,
    metadata_int,
    section_path_hit_count,
)
from src.infrastructure.retrieval.rerankers.deterministic.reranker_noise_penalty import (
    intent_noise_penalty,
    noise_penalty,
)
from src.infrastructure.retrieval.rerankers.deterministic.table_query_evidence_scorer import (
    table_query_evidence_score,
)


class DeterministicHybridReranker(Reranker):
    def __init__(
        self,
        *,
        intent_inferer: RetrievalQueryIntentInferer | None = None,
    ) -> None:
        self.intent_inferer = intent_inferer or RetrievalQueryIntentInferer()

    def rerank(
        self,
        query: RetrievalQuery,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        intent = self.intent_inferer.resolve(query)
        query_terms = extract_query_terms(query.effective_query())
        query_identifiers = {
            identifier.lower()
            for identifier in query.detected_identifiers
            if identifier and identifier.strip()
        }
        query_text = query.effective_query().lower()
        return sorted(
            chunks,
            key=lambda chunk: self._score_chunk(
                query=query,
                chunk=chunk,
                intent=intent,
                query_text=query_text,
                query_terms=query_terms,
                query_identifiers=query_identifiers,
            ),
            reverse=True,
        )

    def _score_chunk(
        self,
        *,
        query: RetrievalQuery,
        chunk: RetrievedChunk,
        intent: RetrievalQueryIntent,
        query_text: str,
        query_terms: list[str],
        query_identifiers: set[str],
    ) -> tuple[float, float, int, int]:
        sql_score = metadata_float(chunk, "sql_keyword_source_score")
        dense_score = metadata_float(chunk, "dense_source_score")
        best_score = metadata_float(chunk, "best_source_score", default=chunk.score)
        structured_match_count = metadata_int(chunk, "structured_match_count")
        identifier_matches = max(
            metadata_int(chunk, "sql_exact_identifier_matches"),
            identifier_match_count(chunk, query_identifiers),
        )
        role = detect_chunk_role(chunk.content)
        section_hit_count = section_path_hit_count(chunk, query_terms)

        score = chunk.score * 8.0
        score += best_score * 4.0
        score += sql_score * 3.0
        score += dense_score * 1.25
        # Structured evidence's own raw score (0.75-3ish, additive per
        # identifier/entity/related-entity hit) is on a different scale than
        # sql_keyword's (frequently 10-70+, several bonuses stacked) or
        # dense's (0-1 cosine similarity) -- best_score alone would leave a
        # structured-only chunk's signal negligible next to even a weak sql
        # hit. structured_match_count is a small integer (how many
        # identifier/entity/related-entity signals hit this chunk), weighted
        # here to be comparable to the other per-signal bonuses below
        # (role/chunk-type-fit/section-hit), not to compete with sql's
        # literal-match bonuses.
        score += float(structured_match_count) * 10.0
        score += identifier_matches * 35.0
        score += role_score(role)
        score += intent_chunk_type_score(
            intent,
            chunk.chunk_type,
            query,
            query_text=query_text,
        )
        score += table_query_evidence_score(
            intent=intent,
            query=query,
            query_text=query_text,
            chunk=chunk,
            role=role,
        )
        score += float(section_hit_count) * 2.5
        score -= noise_penalty(chunk)
        score -= intent_noise_penalty(
            intent=intent,
            chunk_type=chunk.chunk_type,
            query_text=query_text,
            identifier_matches=identifier_matches,
        )

        return (
            score,
            -float(chunk.source.page_start or chunk.source.page_end or 10**6),
            -metadata_int(chunk, "sequence_number"),
            -len(chunk.content or ""),
        )
