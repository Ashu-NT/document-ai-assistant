from dataclasses import dataclass

from src.application.workflows.retrieval.deduplication.retrieved_chunk_signature import (
    detect_chunk_role,
)
from src.domain.retrieval import RetrievalQuery
from src.infrastructure.db.orm_models import ChunkORM, DocumentORM
from src.infrastructure.retrieval.keyword.scoring.sql_keyword_penalties import (
    ancestor_specificity_bonus,
    chunk_role_penalty,
    noise_penalty,
    overview_section_bonus,
)
from src.infrastructure.retrieval.keyword.scoring.sql_keyword_score_components import (
    SqlKeywordIdentifierMatches,
    SqlKeywordSectionMatches,
    build_metadata,
    chunk_type_fit,
    document_text,
    identifier_match_counts,
    primary_type_fit,
    query_identifier_set,
    section_match_counts,
    structured_fit,
)
from src.infrastructure.retrieval.keyword.scoring.sql_keyword_scoring_config import (
    OVERVIEW_QUERY_MARKERS,
)
from src.infrastructure.retrieval.keyword.scoring.sql_keyword_text_helpers import (
    ordered_query_match,
    section_path_parts,
    split_section_path,
)
from src.infrastructure.retrieval.keyword.sql_keyword_query_terms import (
    normalize_query_text,
)


@dataclass(slots=True, frozen=True)
class SqlKeywordScoreBreakdown:
    total_score: float
    metadata: dict[str, str]


class SqlKeywordScorer:
    def score(
        self,
        *,
        row: ChunkORM,
        document: DocumentORM | None,
        retrieval_query: RetrievalQuery | None,
        query_text: str,
        query_terms: list[str],
    ) -> SqlKeywordScoreBreakdown:
        query_identifiers_compact = query_identifier_set(retrieval_query)
        content_text = " \n ".join(part for part in [row.content, row.embedding_text] if part)
        path_parts = section_path_parts(row.section_path)
        section_path_text = " > ".join(path_parts)
        document_text_value = document_text(document)
        normalized_content = normalize_query_text(content_text)
        normalized_query = normalize_query_text(query_text)
        lowered_query = query_text.lower()
        local_parts, ancestor_parts = split_section_path(path_parts)
        normalized_local = normalize_query_text(" > ".join(local_parts))
        normalized_ancestor = normalize_query_text(" > ".join(ancestor_parts))
        chunk_role = detect_chunk_role(row.content)

        identifier_matches = identifier_match_counts(
            identifiers=query_identifiers_compact,
            content_text=content_text,
            section_path_text=section_path_text,
            document_text_value=document_text_value,
        )
        matched_terms = [term for term in query_terms if term in normalized_content]
        exact_phrase_match = bool(normalized_query and normalized_query in normalized_content)
        ordered_match = ordered_query_match(
            normalized_combined=normalized_content,
            query_terms=query_terms,
        )
        section_match = section_match_counts(
            query_terms=query_terms,
            normalized_local=normalized_local,
            normalized_ancestor=normalized_ancestor,
        )
        chunk_type_fit_value = chunk_type_fit(retrieval_query, row.chunk_type)
        primary_type_fit_value = primary_type_fit(retrieval_query, row.chunk_type)
        structured_fit_value = structured_fit(
            retrieval_query=retrieval_query,
            chunk_type=row.chunk_type,
            lowered_query=lowered_query,
        )
        score = self._score_total(
            row=row,
            query_terms=query_terms,
            query_text=query_text,
            lowered_query=lowered_query,
            section_path_text=section_path_text,
            normalized_local=normalized_local,
            normalized_ancestor=normalized_ancestor,
            chunk_role=chunk_role,
            identifier_matches=identifier_matches,
            matched_terms=matched_terms,
            exact_phrase_match=exact_phrase_match,
            ordered_match=ordered_match,
            section_match=section_match,
            chunk_type_fit=chunk_type_fit_value,
            primary_type_fit=primary_type_fit_value,
            structured_fit=structured_fit_value,
        )
        metadata = build_metadata(
            score=score,
            document=document,
            identifier_matches=identifier_matches,
            exact_phrase_match=exact_phrase_match,
            ordered_match=ordered_match,
            chunk_role=chunk_role,
            primary_type_fit_value=primary_type_fit_value,
            section_matches=section_match,
        )
        return SqlKeywordScoreBreakdown(total_score=score, metadata=metadata)

    def _score_total(
        self,
        *,
        row: ChunkORM,
        query_terms: list[str],
        query_text: str,
        lowered_query: str,
        section_path_text: str,
        normalized_local: str,
        normalized_ancestor: str,
        chunk_role: str,
        identifier_matches: SqlKeywordIdentifierMatches,
        matched_terms: list[str],
        exact_phrase_match: bool,
        ordered_match: float,
        section_match: SqlKeywordSectionMatches,
        chunk_type_fit: bool,
        primary_type_fit: bool,
        structured_fit: bool,
    ) -> float:
        score = 0.0
        score += identifier_matches.content_evidence_matches * 22.0
        score += identifier_matches.content_docscope_matches * 4.0
        score += identifier_matches.section_evidence_matches * 10.0
        score += identifier_matches.section_docscope_matches * 3.0
        score += identifier_matches.document_identifier_matches * 2.0

        if identifier_matches.content_evidence_matches > 0:
            score += 6.0
        elif identifier_matches.content_docscope_matches > 0:
            score += 1.0

        if exact_phrase_match:
            score += max(8.0, len(query_terms) * 1.5)
        score += ordered_match
        score += len(matched_terms) * 1.35

        if section_match.local_section_match:
            score += 5.0
            if section_match.ancestor_term_hits > 0:
                score += section_match.ancestor_term_hits * ancestor_specificity_bonus(
                    chunk_type=row.chunk_type,
                    query_text=lowered_query,
                )
        elif section_match.ancestor_section_match:
            score += 1.5

        if any(marker in lowered_query for marker in OVERVIEW_QUERY_MARKERS):
            score += overview_section_bonus(
                normalized_local=normalized_local,
                normalized_ancestor=normalized_ancestor,
            )

        if chunk_type_fit:
            score += 6.0
        if primary_type_fit:
            score += 3.0
        if structured_fit:
            score += 4.0

        score -= chunk_role_penalty(chunk_role)
        score -= noise_penalty(
            chunk_type=row.chunk_type,
            section_path_text=section_path_text,
            content=row.content,
            query_text=query_text,
            exact_identifier_matches=identifier_matches.meaningful_identifier_matches,
        )

        path_depth = len(section_path_parts(row.section_path))
        if path_depth > 8:
            score -= (path_depth - 8) * 0.7
        return score
