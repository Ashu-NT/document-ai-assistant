from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import SparePart
from src.infrastructure.db.mappers import SparePartMapper
from src.infrastructure.db.orm_models import SparePartORM
from src.shared.exceptions import DatabaseError


class SparePartReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_spare_parts(
        self,
        document_id: str | None = None,
    ) -> list[SparePart]:
        try:
            statement = select(SparePartORM)

            if document_id is not None:
                statement = statement.where(
                    SparePartORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [SparePartMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list spare parts.",
                details={"document_id": document_id},
            ) from exc