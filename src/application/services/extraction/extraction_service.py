from src.application.contracts.extraction import ExtractionRepository
from src.application.validation.extraction import ExtractionResultValidator
from src.domain.extraction import ExtractionResult
from src.shared.activity import ActivityContext
from src.shared.execution import ActionResult, tracked_action


class ExtractionService:
    def __init__(
        self,
        extraction_repository: ExtractionRepository,
        extraction_result_validator: ExtractionResultValidator,
    ) -> None:
        self.extraction_repository = extraction_repository
        self.extraction_result_validator = extraction_result_validator

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
        validation = self.extraction_result_validator.validate(result)
        validation.raise_if_invalid()

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
                "supplier_count": len(result.suppliers),
                "confidence_score": result.confidence_score,
                "requires_human_review": result.requires_human_review,
            },
        )

    @tracked_action(
        action="extraction.result_replaced",
        entity_type="document",
        activity=True,
        audit=True,
        event=True,
    )
    def replace_extraction_result(
        self,
        result: ExtractionResult,
        activity_context: ActivityContext | None = None,
    ) -> ActionResult:
        validation = self.extraction_result_validator.validate(result)
        validation.raise_if_invalid()

        self.extraction_repository.replace_extraction_result(result)

        return ActionResult(
            entity_type="document",
            entity_id=result.document_id,
            message="Extraction result replaced.",
            payload={
                "extraction_id": result.extraction_id,
                "document_id": result.document_id,
                "maintenance_task_count": len(result.maintenance_tasks),
                "spare_part_count": len(result.spare_parts),
                "equipment_count": len(result.equipment),
                "manufacturer_count": len(result.manufacturers),
                "supplier_count": len(result.suppliers),
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

    def list_suppliers(self, document_id: str | None = None):
        return self.extraction_repository.list_suppliers(document_id)

    def search_maintenance_tasks(self, query: str, document_id: str | None = None):
        return self.extraction_repository.search_maintenance_tasks(query, document_id)

    def search_spare_parts(self, query: str, document_id: str | None = None):
        return self.extraction_repository.search_spare_parts(query, document_id)

    def search_equipment(self, query: str, document_id: str | None = None):
        return self.extraction_repository.search_equipment(query, document_id)

    def search_manufacturers(self, query: str, document_id: str | None = None):
        return self.extraction_repository.search_manufacturers(query, document_id)

    def search_suppliers(self, query: str, document_id: str | None = None):
        return self.extraction_repository.search_suppliers(query, document_id)
