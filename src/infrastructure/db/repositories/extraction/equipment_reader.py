from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import EquipmentInfo
from src.infrastructure.db.mappers import EquipmentInfoMapper
from src.infrastructure.db.orm_models import EquipmentInfoORM
from src.shared.exceptions import DatabaseError


class EquipmentReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_equipment(
        self,
        document_id: str | None = None,
    ) -> list[EquipmentInfo]:
        try:
            statement = select(EquipmentInfoORM)

            if document_id is not None:
                statement = statement.where(
                    EquipmentInfoORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [EquipmentInfoMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list equipment info.",
                details={"document_id": document_id},
            ) from exc