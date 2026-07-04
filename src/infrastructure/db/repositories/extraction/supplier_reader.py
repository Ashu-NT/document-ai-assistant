from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import Supplier
from src.infrastructure.db.mappers import SupplierMapper
from src.infrastructure.db.orm_models import SupplierORM
from src.shared.exceptions import DatabaseError


class SupplierReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_suppliers(
        self,
        document_id: str | None = None,
    ) -> list[Supplier]:
        try:
            statement = select(SupplierORM)

            if document_id is not None:
                statement = statement.where(
                    SupplierORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [SupplierMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list suppliers.",
                details={"document_id": document_id},
            ) from exc

    def search_suppliers(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[Supplier]:
        try:
            statement = select(SupplierORM).where(
                SupplierORM.name.ilike(f"%{query}%")
            )

            if document_id is not None:
                statement = statement.where(
                    SupplierORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [SupplierMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to search suppliers.",
                details={"query": query, "document_id": document_id},
            ) from exc
