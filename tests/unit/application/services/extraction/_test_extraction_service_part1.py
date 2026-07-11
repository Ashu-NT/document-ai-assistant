import pytest

from src.application.services.extraction import ExtractionService

from src.application.validation.extraction import ExtractionResultValidator

from src.shared.exceptions import SchemaValidationError

class FakeExtractionRepository:
    def __init__(self) -> None:
        self.results = {}
        self.replace_calls = []
        self.semantic_relationships: dict[str, list] = {}
        self.replace_semantic_relationships_calls = []

    def save_extraction_result(self, result) -> None:
        self.results[result.extraction_id] = result

    def replace_extraction_result(self, result) -> None:
        self.replace_calls.append(result)
        self.results = {
            extraction_id: existing
            for extraction_id, existing in self.results.items()
            if existing.document_id != result.document_id
        }
        self.results[result.extraction_id] = result

    def get_extraction_result(self, extraction_id: str):
        return self.results.get(extraction_id)

    def get_document_extraction_result(self, document_id: str):
        for result in reversed(list(self.results.values())):
            if result.document_id == document_id:
                return result
        return None

    def list_maintenance_tasks(self, document_id: str | None = None):
        return [
            task
            for result in self.results.values()
            for task in result.maintenance_tasks
            if document_id is None or task.document_id == document_id
        ]

    def list_spare_parts(self, document_id: str | None = None):
        return [
            part
            for result in self.results.values()
            for part in result.spare_parts
            if document_id is None or part.document_id == document_id
        ]

    def list_equipment(self, document_id: str | None = None):
        return [
            equipment
            for result in self.results.values()
            for equipment in result.equipment
            if document_id is None or equipment.document_id == document_id
        ]

    def list_manufacturers(self, document_id: str | None = None):
        return [
            manufacturer
            for result in self.results.values()
            for manufacturer in result.manufacturers
            if document_id is None or manufacturer.document_id == document_id
        ]

    def list_suppliers(self, document_id: str | None = None):
        return [
            supplier
            for result in self.results.values()
            for supplier in result.suppliers
            if document_id is None or supplier.document_id == document_id
        ]

    def list_contact_points(self, document_id: str | None = None):
        return [
            contact_point
            for result in self.results.values()
            for contact_point in result.contact_points
            if document_id is None or contact_point.document_id == document_id
        ]

    def list_procedures(self, document_id: str | None = None):
        return [
            procedure
            for result in self.results.values()
            for procedure in result.procedures
            if document_id is None or procedure.document_id == document_id
        ]

    def list_specifications(self, document_id: str | None = None):
        return [
            specification
            for result in self.results.values()
            for specification in result.specifications
            if document_id is None or specification.document_id == document_id
        ]

    def list_safety_warnings(self, document_id: str | None = None):
        return [
            safety_warning
            for result in self.results.values()
            for safety_warning in result.safety_warnings
            if document_id is None or safety_warning.document_id == document_id
        ]

    def list_maintenance_intervals(self, document_id: str | None = None):
        return [
            maintenance_interval
            for result in self.results.values()
            for maintenance_interval in result.maintenance_intervals
            if document_id is None or maintenance_interval.document_id == document_id
        ]

    def list_troubleshooting_entries(self, document_id: str | None = None):
        return [
            troubleshooting_entry
            for result in self.results.values()
            for troubleshooting_entry in result.troubleshooting_entries
            if document_id is None or troubleshooting_entry.document_id == document_id
        ]

    def list_semantic_relationships(self, document_id: str | None = None):
        if document_id is None:
            return [
                relationship
                for relationships in self.semantic_relationships.values()
                for relationship in relationships
            ]
        return self.semantic_relationships.get(document_id, [])

    def replace_semantic_relationships(self, document_id: str, relationships: list) -> None:
        self.replace_semantic_relationships_calls.append((document_id, relationships))
        self.semantic_relationships[document_id] = relationships

def make_service(repository: FakeExtractionRepository) -> ExtractionService:
    return ExtractionService(
        repository,
        ExtractionResultValidator(),
    )

def test_save_extraction_result(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    service = make_service(repository)

    result = service.save_extraction_result(sample_extraction_result)

    assert result.entity_id == sample_extraction_result.document_id
    assert result.payload["extraction_id"] == sample_extraction_result.extraction_id
    assert result.payload["maintenance_task_count"] == 1
    assert result.payload["supplier_count"] == 1
    assert result.payload["procedure_count"] == 1
    assert result.payload["specification_count"] == 1
    assert result.payload["safety_warning_count"] == 1
    assert result.payload["maintenance_interval_count"] == 1
    assert result.payload["troubleshooting_entry_count"] == 1
    assert len(repository.results) == 1

def test_get_extraction_result(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = make_service(repository)

    loaded = service.get_extraction_result(sample_extraction_result.extraction_id)

    assert loaded == sample_extraction_result

def test_get_document_extraction_result(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = make_service(repository)

    loaded = service.get_document_extraction_result(sample_extraction_result.document_id)

    assert loaded == sample_extraction_result

def test_list_maintenance_tasks(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = make_service(repository)

    tasks = service.list_maintenance_tasks(sample_extraction_result.document_id)

    assert len(tasks) == 1

def test_list_spare_parts(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = make_service(repository)

    parts = service.list_spare_parts(sample_extraction_result.document_id)

    assert len(parts) == 1

def test_list_equipment(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = make_service(repository)

    equipment = service.list_equipment(sample_extraction_result.document_id)

    assert len(equipment) == 1

def test_list_manufacturers(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = make_service(repository)

    manufacturers = service.list_manufacturers(sample_extraction_result.document_id)

    assert len(manufacturers) == 1

def test_list_suppliers(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = make_service(repository)

    suppliers = service.list_suppliers(sample_extraction_result.document_id)

    assert len(suppliers) == 1

def test_list_contact_points(sample_extraction_result, sample_contact_point) -> None:
    repository = FakeExtractionRepository()
    sample_extraction_result.contact_points = [sample_contact_point]
    repository.save_extraction_result(sample_extraction_result)

    service = make_service(repository)

    contact_points = service.list_contact_points(sample_extraction_result.document_id)

    assert len(contact_points) == 1
    assert contact_points[0].value == "service@example.com"

def test_list_procedures(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = make_service(repository)

    procedures = service.list_procedures(sample_extraction_result.document_id)

    assert len(procedures) == 1

def test_list_specifications(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = make_service(repository)

    specifications = service.list_specifications(sample_extraction_result.document_id)

    assert len(specifications) == 1

def test_list_safety_warnings(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = make_service(repository)

    safety_warnings = service.list_safety_warnings(sample_extraction_result.document_id)

    assert len(safety_warnings) == 1

def test_list_maintenance_intervals(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = make_service(repository)

    maintenance_intervals = service.list_maintenance_intervals(
        sample_extraction_result.document_id
    )

    assert len(maintenance_intervals) == 1
