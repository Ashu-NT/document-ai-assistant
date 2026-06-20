import re

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.retrieval import RetrievalQuery, RetrievedChunk
from src.infrastructure.db.mappers import RetrievedChunkMapper
from src.infrastructure.db.orm_models import ChunkORM, DocumentORM
from src.shared.exceptions import DatabaseError

_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "be",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "should",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "which",
    "with",
}


class SqlKeywordRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def search_chunks(
        self,
        query: RetrievalQuery | str,
        limit: int | None = None,
    ) -> list[RetrievedChunk]:
        try:
            retrieval_query = (
                query
                if isinstance(query, RetrievalQuery)
                else None
            )
            query_text = (
                retrieval_query.effective_query()
                if retrieval_query is not None
                else str(query)
            ).strip()
            result_limit = (
                retrieval_query.top_k
                if retrieval_query is not None
                else (limit or 5)
            )

            if not query_text:
                return []

            query_terms = self._extract_terms(query_text)
            if not query_terms:
                query_terms = [query_text.lower()]

            statement = self._build_statement(
                query_text=query_text,
                query_terms=query_terms,
                retrieval_query=retrieval_query,
                result_limit=result_limit,
            )
            rows = self.session.execute(statement).scalars().all()
            scored_rows = sorted(
                (
                    (
                        row,
                        self._score_row(
                            row=row,
                            query_text=query_text,
                            query_terms=query_terms,
                        ),
                    )
                    for row in rows
                ),
                key=lambda item: item[1],
                reverse=True,
            )

            return [
                RetrievedChunkMapper.from_chunk_orm(
                    row,
                    score=score,
                    retrieval_source="sql_keyword",
                )
                for row, score in scored_rows[:result_limit]
                if score > 0
            ]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to search chunks by SQL keyword.",
                details={
                    "query": str(query),
                    "limit": limit,
                },
            ) from exc

    def _build_statement(
        self,
        *,
        query_text: str,
        query_terms: list[str],
        retrieval_query: RetrievalQuery | None,
        result_limit: int,
    ):
        patterns = [f"%{query_text}%"]
        patterns.extend(f"%{term}%" for term in query_terms)

        text_clauses = [
            or_(
                ChunkORM.content.ilike(pattern),
                ChunkORM.embedding_text.ilike(pattern),
            )
            for pattern in patterns
        ]
        conditions = [or_(*text_clauses)]
        statement = select(ChunkORM)

        if retrieval_query is not None and retrieval_query.document_types:
            statement = statement.join(
                DocumentORM,
                DocumentORM.id == ChunkORM.document_id,
            )
            conditions.append(
                DocumentORM.document_type.in_(
                    [document_type.value for document_type in retrieval_query.document_types]
                )
            )

        if retrieval_query is not None and retrieval_query.chunk_types:
            conditions.append(
                ChunkORM.chunk_type.in_(
                    [chunk_type.value for chunk_type in retrieval_query.chunk_types]
                )
            )

        candidate_limit = max(result_limit * 5, result_limit)
        return statement.where(and_(*conditions)).limit(candidate_limit)

    @staticmethod
    def _extract_terms(query_text: str) -> list[str]:
        return [
            term
            for term in re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]*", query_text.lower())
            if len(term) > 1 and term not in _STOP_WORDS
        ]

    def _score_row(
        self,
        *,
        row: ChunkORM,
        query_text: str,
        query_terms: list[str],
    ) -> float:
        haystack = " ".join(
            part
            for part in [row.content, row.embedding_text]
            if part
        ).lower()
        if not haystack:
            return 0.0

        score = 0.0
        if query_text.lower() in haystack:
            score += max(2.0, len(query_terms) * 0.75)

        for term in query_terms:
            if term in haystack:
                score += 1.0

        return score
