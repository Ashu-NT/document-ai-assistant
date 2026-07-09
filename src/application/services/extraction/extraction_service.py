from src.application.contracts.extraction import ExtractionRepository
from src.application.validation.extraction import ExtractionResultValidator
from src.domain.extraction import ExtractionResult, SemanticRelationship
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
                "contact_point_count": len(result.contact_points),
                "procedure_count": len(result.procedures),
                "specification_count": len(result.specifications),
                "safety_warning_count": len(result.safety_warnings),
                "maintenance_interval_count": len(result.maintenance_intervals),
                "troubleshooting_entry_count": len(result.troubleshooting_entries),
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
                "contact_point_count": len(result.contact_points),
                "procedure_count": len(result.procedures),
                "specification_count": len(result.specifications),
                "safety_warning_count": len(result.safety_warnings),
                "maintenance_interval_count": len(result.maintenance_intervals),
                "troubleshooting_entry_count": len(result.troubleshooting_entries),
                "confidence_score": result.confidence_score,
                "requires_human_review": result.requires_human_review,
            },
        )

    def get_extraction_result(
        self,
        extraction_id: str,
    ) -> ExtractionResult | None:
        return self.extraction_repository.get_extraction_result(extraction_id)

    def get_document_extraction_result(
        self,
        document_id: str,
    ) -> ExtractionResult | None:
        return self.extraction_repository.get_document_extraction_result(document_id)

    def has_extraction_result(self, document_id: str) -> bool:
        return self.extraction_repository.has_extraction_result(document_id)

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

    def list_contact_points(self, document_id: str | None = None):
        return self.extraction_repository.list_contact_points(document_id)

    def list_procedures(self, document_id: str | None = None):
        return self.extraction_repository.list_procedures(document_id)

    def list_specifications(self, document_id: str | None = None):
        return self.extraction_repository.list_specifications(document_id)

    def list_safety_warnings(self, document_id: str | None = None):
        return self.extraction_repository.list_safety_warnings(document_id)

    def list_maintenance_intervals(self, document_id: str | None = None):
        return self.extraction_repository.list_maintenance_intervals(document_id)

    def list_troubleshooting_entries(self, document_id: str | None = None):
        return self.extraction_repository.list_troubleshooting_entries(document_id)

    def list_maintenance_intervals_by_task_id(self, maintenance_task_id: str):
        return self.extraction_repository.list_maintenance_intervals_by_task_id(
            maintenance_task_id
        )

    def list_procedures_by_equipment_id(self, equipment_id: str):
        return self.extraction_repository.list_procedures_by_equipment_id(equipment_id)

    def list_troubleshooting_entries_by_equipment_id(self, equipment_id: str):
        return self.extraction_repository.list_troubleshooting_entries_by_equipment_id(
            equipment_id
        )

    def list_semantic_relationships(self, document_id: str | None = None):
        return self.extraction_repository.list_semantic_relationships(document_id)

    @tracked_action(
        action="extraction.semantic_relationships_replaced",
        entity_type="document",
        activity=True,
        audit=True,
        event=True,
    )
    def replace_semantic_relationships(
        self,
        document_id: str,
        relationships: list[SemanticRelationship],
        activity_context: ActivityContext | None = None,
    ) -> ActionResult:
        self.extraction_repository.replace_semantic_relationships(
            document_id, relationships
        )

        return ActionResult(
            entity_type="document",
            entity_id=document_id,
            message="Semantic relationships replaced.",
            payload={
                "document_id": document_id,
                "relationship_count": len(relationships),
            },
        )

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

    def search_contact_points(self, query: str, document_id: str | None = None):
        return self.extraction_repository.search_contact_points(query, document_id)

    def search_procedures(self, query: str, document_id: str | None = None):
        return self.extraction_repository.search_procedures(query, document_id)

    def search_specifications(self, query: str, document_id: str | None = None):
        return self.extraction_repository.search_specifications(query, document_id)

    def search_safety_warnings(self, query: str, document_id: str | None = None):
        return self.extraction_repository.search_safety_warnings(query, document_id)

    def search_maintenance_intervals(self, query: str, document_id: str | None = None):
        return self.extraction_repository.search_maintenance_intervals(
            query, document_id
        )

    def search_troubleshooting_entries(self, query: str, document_id: str | None = None):
        return self.extraction_repository.search_troubleshooting_entries(
            query, document_id
        )
