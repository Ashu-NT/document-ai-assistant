import pytest

from src.application.services.extraction import ExtractionService
from src.application.validation.extraction import ExtractionResultValidator
from src.shared.exceptions import SchemaValidationError


class FakeExtractionRepository:
    def __init__(self) -> None:
        self.results = {}
        self.replace_calls = []

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
    assert len(repository.results) == 1


def test_get_extraction_result(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = make_service(repository)

    loaded = service.get_extraction_result(sample_extraction_result.extraction_id)

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


def test_save_extraction_result_rejects_invalid_input(
    sample_extraction_result,
) -> None:
    repository = FakeExtractionRepository()
    service = make_service(repository)
    sample_extraction_result.confidence_score = 1.5

    with pytest.raises(SchemaValidationError):
        service.save_extraction_result(sample_extraction_result)

    assert repository.results == {}


def test_replace_extraction_result(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)
    service = make_service(repository)

    replacement = sample_extraction_result.__class__(
        extraction_id="extraction_002",
        document_id=sample_extraction_result.document_id,
        confidence_score=0.7,
    )

    result = service.replace_extraction_result(replacement)

    assert result.entity_id == replacement.document_id
    assert result.payload["extraction_id"] == "extraction_002"
    assert repository.replace_calls == [replacement]
    assert list(repository.results) == ["extraction_002"]


def test_replace_extraction_result_rejects_invalid_input(
    sample_extraction_result,
) -> None:
    repository = FakeExtractionRepository()
    service = make_service(repository)
    sample_extraction_result.confidence_score = 1.5

    with pytest.raises(SchemaValidationError):
        service.replace_extraction_result(sample_extraction_result)

    assert repository.replace_calls == []
