from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.document.entities import Identifier
from src.infrastructure.db.mappers import IdentifierMapper
from src.infrastructure.db.orm_models import IdentifierORM
from src.shared.exceptions import DatabaseError


class IdentifierReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def search_identifiers(self, value: str) -> list[Identifier]:
        try:
            normalized = value.strip().upper().replace(" ", "")
            statement = select(IdentifierORM).where(
                IdentifierORM.normalized_value == normalized,
            )
            rows = self.session.execute(statement).scalars().all()
            return [IdentifierMapper.to_domain(row) for row in rows]
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to search identifiers.",
                details={"value": value},
            ) from exc

    def search_by_type(self, identifier_type: str, document_id: str) -> list[Identifier]:
        try:
            statement = select(IdentifierORM).where(
                IdentifierORM.identifier_type == identifier_type,
                IdentifierORM.document_id == document_id,
            )
            rows = self.session.execute(statement).scalars().all()
            return [IdentifierMapper.to_domain(row) for row in rows]
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to search identifiers by type.",
                details={"identifier_type": identifier_type, "document_id": document_id},
            ) from exc

    def get_identifiers_for_chunk(self, chunk_id: str) -> list[Identifier]:
        try:
            statement = select(IdentifierORM).where(
                IdentifierORM.chunk_id == chunk_id,
            )
            rows = self.session.execute(statement).scalars().all()
            return [IdentifierMapper.to_domain(row) for row in rows]
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to get identifiers for chunk.",
                details={"chunk_id": chunk_id},
            ) from exc
