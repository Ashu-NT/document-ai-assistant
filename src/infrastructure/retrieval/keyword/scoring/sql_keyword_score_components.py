from dataclasses import dataclass

from src.domain.retrieval import RetrievalQuery
from src.infrastructure.db.orm_models import DocumentORM
from src.infrastructure.retrieval.keyword.scoring.sql_keyword_morphology import (
    contains_compact_id,
    section_path_hit,
)
from src.infrastructure.retrieval.keyword.scoring.sql_keyword_scoring_config import (
    STRUCTURED_TYPES,
)
from src.shared.text.alnum_tokenizer import compact_alnum


@dataclass(slots=True, frozen=True)
class SqlKeywordIdentifierMatches:
    content_identifier_matches: int
    content_evidence_matches: int
    content_docscope_matches: int
    section_identifier_matches: int
    section_evidence_matches: int
    section_docscope_matches: int
    document_identifier_matches: int
    total_identifier_matches: int
    meaningful_identifier_matches: int


@dataclass(slots=True, frozen=True)
class SqlKeywordSectionMatches:
    local_term_hits: int
    ancestor_term_hits: int
    local_section_match: bool
    ancestor_section_match: bool
    section_path_match: bool


def query_identifier_set(retrieval_query: RetrievalQuery | None) -> set[str]:
    if retrieval_query is None:
        return set()
    return {
        compact_alnum(identifier)
        for identifier in retrieval_query.detected_identifiers
        if identifier and identifier.strip()
    } - {""}


def document_text(document: DocumentORM | None) -> str:
    if document is None:
        return ""
    return " \n ".join(
        part for part in [document.title or "", document.file_name or ""] if part
    )


def identifier_match_counts(
    *,
    identifiers: set[str],
    content_text: str,
    section_path_text: str,
    document_text_value: str,
) -> SqlKeywordIdentifierMatches:
    document_scope_identifiers = {
        identifier
        for identifier in identifiers
        if contains_compact_id(identifier, document_text_value)
    }
    content_identifier_matches = sum(
        1 for identifier in identifiers if contains_compact_id(identifier, content_text)
    )
    content_evidence_matches = sum(
        1
        for identifier in identifiers
        if identifier not in document_scope_identifiers
        and contains_compact_id(identifier, content_text)
    )
    section_identifier_matches = sum(
        1
        for identifier in identifiers
        if not contains_compact_id(identifier, content_text)
        and contains_compact_id(identifier, section_path_text)
    )
    section_evidence_matches = sum(
        1
        for identifier in identifiers
        if identifier not in document_scope_identifiers
        and not contains_compact_id(identifier, content_text)
        and contains_compact_id(identifier, section_path_text)
    )
    document_identifier_matches = sum(
        1
        for identifier in identifiers
        if not contains_compact_id(identifier, content_text)
        and not contains_compact_id(identifier, section_path_text)
        and contains_compact_id(identifier, document_text_value)
    )
    return SqlKeywordIdentifierMatches(
        content_identifier_matches=content_identifier_matches,
        content_evidence_matches=content_evidence_matches,
        content_docscope_matches=content_identifier_matches - content_evidence_matches,
        section_identifier_matches=section_identifier_matches,
        section_evidence_matches=section_evidence_matches,
        section_docscope_matches=section_identifier_matches - section_evidence_matches,
        document_identifier_matches=document_identifier_matches,
        total_identifier_matches=(
            content_identifier_matches
            + section_identifier_matches
            + document_identifier_matches
        ),
        meaningful_identifier_matches=(
            content_identifier_matches + section_identifier_matches
        ),
    )


def section_match_counts(
    *,
    query_terms: list[str],
    normalized_local: str,
    normalized_ancestor: str,
) -> SqlKeywordSectionMatches:
    threshold = min(2, len(query_terms))
    padded_local = f" {normalized_local} "
    padded_ancestor = f" {normalized_ancestor} "
    local_term_hits = sum(1 for term in query_terms if section_path_hit(term, padded_local))
    ancestor_term_hits = sum(
        1 for term in query_terms if section_path_hit(term, padded_ancestor)
    )
    local_section_match = bool(query_terms and local_term_hits >= threshold)
    ancestor_section_match = bool(
        query_terms and not local_section_match and ancestor_term_hits >= threshold
    )
    return SqlKeywordSectionMatches(
        local_term_hits=local_term_hits,
        ancestor_term_hits=ancestor_term_hits,
        local_section_match=local_section_match,
        ancestor_section_match=ancestor_section_match,
        section_path_match=local_section_match or ancestor_section_match,
    )


def chunk_type_fit(
    retrieval_query: RetrievalQuery | None,
    chunk_type: str,
) -> bool:
    return bool(
        retrieval_query is not None
        and retrieval_query.chunk_types
        and chunk_type in {candidate.value for candidate in retrieval_query.chunk_types}
    )


def primary_type_fit(
    retrieval_query: RetrievalQuery | None,
    chunk_type: str,
) -> bool:
    return bool(
        retrieval_query is not None
        and retrieval_query.chunk_types
        and chunk_type == retrieval_query.chunk_types[0].value
    )


def structured_fit(
    *,
    retrieval_query: RetrievalQuery | None,
    chunk_type: str,
    lowered_query: str,
) -> bool:
    return bool(
        retrieval_query is not None
        and chunk_type in STRUCTURED_TYPES
        and (
            retrieval_query.has_identifiers()
            or any(
                marker in lowered_query
                for marker in (
                    "spec",
                    "specification",
                    "table",
                    "parts list",
                    "certificate",
                    "approval",
                    "iecex",
                    "atex",
                )
            )
        )
    )


def build_metadata(
    *,
    score: float,
    document: DocumentORM | None,
    identifier_matches: SqlKeywordIdentifierMatches,
    exact_phrase_match: bool,
    ordered_match: float,
    chunk_role: str,
    primary_type_fit_value: bool,
    section_matches: SqlKeywordSectionMatches,
) -> dict[str, str]:
    metadata = {
        "sql_keyword_source_score": f"{score:.6f}",
        "sql_exact_identifier_matches": str(identifier_matches.total_identifier_matches),
        "sql_content_identifier_matches": str(
            identifier_matches.content_identifier_matches
        ),
        "sql_content_evidence_matches": str(identifier_matches.content_evidence_matches),
        "sql_content_docscope_matches": str(identifier_matches.content_docscope_matches),
        "sql_section_identifier_matches": str(
            identifier_matches.section_identifier_matches
        ),
        "sql_document_identifier_matches": str(
            identifier_matches.document_identifier_matches
        ),
        "sql_exact_phrase_match": str(exact_phrase_match).lower(),
        "sql_section_path_match": str(section_matches.section_path_match).lower(),
        "sql_local_section_match": str(section_matches.local_section_match).lower(),
        "sql_ordered_match_bonus": f"{ordered_match:.6f}",
        "sql_chunk_role": chunk_role,
        "sql_primary_type_fit": str(primary_type_fit_value).lower(),
    }
    if document is not None:
        metadata["document_type"] = document.document_type
    return metadata
