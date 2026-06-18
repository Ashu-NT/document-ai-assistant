from src.application.contracts.extraction import ExtractionRepository
from src.domain.extraction import ExtractionResult
from src.shared.activity import ActivityContext
from src.shared.execution import ActionResult, tracked_action


class ExtractionService:
    def __init__(self, extraction_repository: ExtractionRepository) -> None:
        self.extraction_repository = extraction_repository

    @tracked_action(
        action="extraction.result_saved",
        entity_type="document",
        activity=True,
        audit=True,
        event=True,
    )
    def save_extraction_result(
        self,
        result: ExtractionResult,
        activity_context: ActivityContext | None = None,
    ) -> ActionResult:
        self.extraction_repository.save_extraction_result(result)

        return ActionResult(
            entity_type="document",
            entity_id=result.document_id,
            message="Extraction result saved.",
            payload={
                "extraction_id": result.extraction_id,
                "document_id": result.document_id,
                "maintenance_task_count": len(result.maintenance_tasks),
                "spare_part_count": len(result.spare_parts),
                "equipment_count": len(result.equipment),
                "manufacturer_count": len(result.manufacturers),
                "confidence_score": result.confidence_score,
                "requires_human_review": result.requires_human_review,
            },
        )

    def get_extraction_result(
        self,
        extraction_id: str,
    ) -> ExtractionResult | None:
        return self.extraction_repository.get_extraction_result(extraction_id)

    def list_maintenance_tasks(self, document_id: str | None = None):
        return self.extraction_repository.list_maintenance_tasks(document_id)

    def list_spare_parts(self, document_id: str | None = None):
        return self.extraction_repository.list_spare_parts(document_id)

    def list_equipment(self, document_id: str | None = None):
        return self.extraction_repository.list_equipment(document_id)

    def list_manufacturers(self, document_id: str | None = None):
        return self.extraction_repository.list_manufacturers(document_id)