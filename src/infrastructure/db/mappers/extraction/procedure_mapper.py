import json

from src.domain.extraction import Procedure
from src.infrastructure.db.mappers.common.source_location_mapper import (
    columns_to_source_location,
)
from src.infrastructure.db.orm_models import ProcedureORM


class ProcedureMapper:
    @staticmethod
    def to_orm(
        procedure: Procedure,
        extraction_id: str | None = None,
    ) -> ProcedureORM:
        return ProcedureORM(
            id=procedure.procedure_id,
            extraction_id=extraction_id,
            document_id=procedure.document_id,
            title=procedure.title,
            steps_json=json.dumps(procedure.steps),
            component_name=procedure.component_name,
            equipment_id=procedure.equipment_id,
            source_chunk_id=procedure.source_chunk_id,
            page_start=procedure.source.page_start,
            page_end=procedure.source.page_end,
            confidence_score=procedure.confidence_score,
            requires_human_review=procedure.requires_human_review,
            created_at=procedure.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: ProcedureORM) -> Procedure:
        try:
            steps = json.loads(orm.steps_json)
        except (TypeError, ValueError):
            steps = []
        return Procedure(
            procedure_id=orm.id,
            document_id=orm.document_id,
            title=orm.title,
            steps=list(steps) if isinstance(steps, list) else [],
            component_name=orm.component_name,
            equipment_id=orm.equipment_id,
            source_chunk_id=orm.source_chunk_id,
            source=columns_to_source_location(
                page_start=orm.page_start,
                page_end=orm.page_end,
            ),
            confidence_score=orm.confidence_score,
            requires_human_review=orm.requires_human_review,
        )
