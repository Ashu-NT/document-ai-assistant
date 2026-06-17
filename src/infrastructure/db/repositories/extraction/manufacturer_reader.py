from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import Manufacturer
from src.infrastructure.db.mappers import ManufacturerMapper
from src.infrastructure.db.orm_models import ManufacturerORM
from src.shared.exceptions import DatabaseError


class ManufacturerReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_manufacturers(
        self,
        document_id: str | None = None,
    ) -> list[Manufacturer]:
        try:
            statement = select(ManufacturerORM)

            if document_id is not None:
                statement = statement.where(
                    ManufacturerORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [ManufacturerMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list manufacturers.",
                details={"document_id": document_id},
            ) from exc