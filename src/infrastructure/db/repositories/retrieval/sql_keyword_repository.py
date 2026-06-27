from sqlalchemy import and_, case, literal, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.retrieval import RetrievalQuery, RetrievedChunk
from src.infrastructure.db.mappers import RetrievedChunkMapper
from src.infrastructure.db.orm_models import ChunkORM, DocumentORM
from src.infrastructure.retrieval.keyword.sql_keyword_query_terms import (
    extract_query_terms,
)
from src.infrastructure.retrieval.keyword.sql_keyword_scorer import (
    SqlKeywordScorer,
    expand_query_terms_with_morph_variants,
)
from src.shared.exceptions import DatabaseError


class SqlKeywordRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.scorer = SqlKeywordScorer()

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

            query_terms = extract_query_terms(query_text)
            if not query_terms:
                query_terms = [query_text.lower()]

            statement = self._build_statement(
                query_text=query_text,
                query_terms=query_terms,
                retrieval_query=retrieval_query,
                result_limit=result_limit,
            )
            rows = self.session.execute(statement).all()
            scored_rows = sorted(
                (
                    (
                        chunk_row,
                        document_row,
                        self.scorer.score(
                            row=chunk_row,
                            document=document_row,
                            retrieval_query=retrieval_query,
                            query_text=query_text,
                            query_terms=query_terms,
                        ),
                    )
                    for chunk_row, document_row in rows
                ),
                key=lambda item: item[2].total_score,
                reverse=True,
            )

            return [
                RetrievedChunkMapper.from_chunk_orm(
                    row,
                    score=score_breakdown.total_score,
                    retrieval_source="sql_keyword",
                    extra_metadata=score_breakdown.metadata,
                )
                for row, _document_row, score_breakdown in scored_rows[:result_limit]
                if score_breakdown.total_score > 0
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
        expanded_terms = expand_query_terms_with_morph_variants(query_terms)
        exact_patterns = [f"%{query_text}%"]
        term_patterns = [f"%{term}%" for term in expanded_terms]
        identifier_patterns = (
            [
                f"%{identifier}%"
                for identifier in retrieval_query.detected_identifiers
                if identifier
            ]
            if retrieval_query is not None
            else []
        )
        patterns = [*exact_patterns, *term_patterns, *identifier_patterns]

        text_clauses = [
            or_(
                ChunkORM.content.ilike(pattern),
                ChunkORM.embedding_text.ilike(pattern),
                ChunkORM.section_path.ilike(pattern),
                DocumentORM.title.ilike(pattern),
                DocumentORM.file_name.ilike(pattern),
            )
            for pattern in patterns
        ]
        conditions = [or_(*text_clauses)]
        statement = (
            select(ChunkORM, DocumentORM)
            .join(DocumentORM, DocumentORM.id == ChunkORM.document_id)
        )

        if retrieval_query is not None and retrieval_query.document_types:
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

        if retrieval_query is not None and retrieval_query.document_id:
            conditions.append(ChunkORM.document_id == retrieval_query.document_id)

        candidate_limit = max(result_limit * 20, 50)
        candidate_order = self._candidate_order_expression(
            exact_patterns=exact_patterns,
            term_patterns=term_patterns,
            identifier_patterns=identifier_patterns,
            retrieval_query=retrieval_query,
        )
        return (
            statement.where(and_(*conditions))
            .order_by(
                candidate_order.desc(),
                ChunkORM.page_start.asc(),
                ChunkORM.sequence_number.asc(),
            )
            .limit(candidate_limit)
        )

    @staticmethod
    def _candidate_order_expression(
        *,
        exact_patterns: list[str],
        term_patterns: list[str],
        identifier_patterns: list[str],
        retrieval_query: RetrievalQuery | None,
    ):
        score = literal(0)

        for pattern in exact_patterns:
            score += case((ChunkORM.content.ilike(pattern), 40), else_=0)
            score += case((ChunkORM.embedding_text.ilike(pattern), 36), else_=0)
            score += case((ChunkORM.section_path.ilike(pattern), 24), else_=0)
            score += case((DocumentORM.title.ilike(pattern), 12), else_=0)
            score += case((DocumentORM.file_name.ilike(pattern), 10), else_=0)

        for pattern in identifier_patterns:
            score += case((ChunkORM.content.ilike(pattern), 24), else_=0)
            score += case((ChunkORM.embedding_text.ilike(pattern), 20), else_=0)
            score += case((ChunkORM.section_path.ilike(pattern), 14), else_=0)
            score += case((DocumentORM.title.ilike(pattern), 6), else_=0)
            score += case((DocumentORM.file_name.ilike(pattern), 6), else_=0)

        for pattern in term_patterns:
            score += case((ChunkORM.content.ilike(pattern), 4), else_=0)
            score += case((ChunkORM.embedding_text.ilike(pattern), 4), else_=0)
            score += case((ChunkORM.section_path.ilike(pattern), 3), else_=0)
            score += case((DocumentORM.title.ilike(pattern), 1), else_=0)
            score += case((DocumentORM.file_name.ilike(pattern), 1), else_=0)

        if retrieval_query is not None:
            for index, chunk_type in enumerate(retrieval_query.chunk_types[:6]):
                score += case(
                    (ChunkORM.chunk_type == chunk_type.value, max(6 - index, 1)),
                    else_=0,
                )
            for index, document_type in enumerate(retrieval_query.document_types[:4]):
                score += case(
                    (DocumentORM.document_type == document_type.value, max(4 - index, 1)),
                    else_=0,
                )

        return score
