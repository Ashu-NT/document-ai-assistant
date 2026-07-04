from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import Procedure
from src.infrastructure.db.mappers import ProcedureMapper
from src.infrastructure.db.orm_models import ProcedureORM
from src.shared.exceptions import DatabaseError


class ProcedureReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_procedures(
        self,
        document_id: str | None = None,
    ) -> list[Procedure]:
        try:
            statement = select(ProcedureORM)

            if document_id is not None:
                statement = statement.where(
                    ProcedureORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [ProcedureMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list procedures.",
                details={"document_id": document_id},
            ) from exc

    def list_by_equipment_id(
        self,
        equipment_id: str,
    ) -> list[Procedure]:
        try:
            statement = select(ProcedureORM).where(
                ProcedureORM.equipment_id == equipment_id
            )

            rows = self.session.execute(statement).scalars().all()

            return [ProcedureMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list procedures for equipment.",
                details={"equipment_id": equipment_id},
            ) from exc

    def search_procedures(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[Procedure]:
        try:
            pattern = f"%{query}%"
            statement = select(ProcedureORM).where(
                or_(
                    ProcedureORM.title.ilike(pattern),
                    ProcedureORM.component_name.ilike(pattern),
                )
            )

            if document_id is not None:
                statement = statement.where(
                    ProcedureORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [ProcedureMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to search procedures.",
                details={"query": query, "document_id": document_id},
            ) from exc
