from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.document.entities import Identifier
from src.infrastructure.db.mappers.document.identifier_mapper import IdentifierMapper
from src.infrastructure.db.orm_models import IdentifierORM


class IdentifierReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def search_identifiers(self, value: str) -> list[Identifier]:
        normalized = value.strip().upper().replace(" ", "")

        statement = select(IdentifierORM).where(
            IdentifierORM.normalized_value == normalized,
        )

        rows = self.session.execute(statement).scalars().all()

        return [IdentifierMapper.to_domain(row) for row in rows]