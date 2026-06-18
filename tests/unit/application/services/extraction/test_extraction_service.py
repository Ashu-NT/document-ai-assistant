from src.application.services.extraction import ExtractionService


class FakeExtractionRepository:
    def __init__(self) -> None:
        self.results = {}

    def save_extraction_result(self, result) -> None:
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


def test_save_extraction_result(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    service = ExtractionService(repository)

    result = service.save_extraction_result(sample_extraction_result)

    assert result.entity_id == sample_extraction_result.document_id
    assert result.payload["extraction_id"] == sample_extraction_result.extraction_id
    assert result.payload["maintenance_task_count"] == 1
    assert len(repository.results) == 1


def test_get_extraction_result(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = ExtractionService(repository)

    loaded = service.get_extraction_result(sample_extraction_result.extraction_id)

    assert loaded == sample_extraction_result


def test_list_maintenance_tasks(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = ExtractionService(repository)

    tasks = service.list_maintenance_tasks(sample_extraction_result.document_id)

    assert len(tasks) == 1


def test_list_spare_parts(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = ExtractionService(repository)

    parts = service.list_spare_parts(sample_extraction_result.document_id)

    assert len(parts) == 1


def test_list_equipment(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = ExtractionService(repository)

    equipment = service.list_equipment(sample_extraction_result.document_id)

    assert len(equipment) == 1


def test_list_manufacturers(sample_extraction_result) -> None:
    repository = FakeExtractionRepository()
    repository.save_extraction_result(sample_extraction_result)

    service = ExtractionService(repository)

    manufacturers = service.list_manufacturers(sample_extraction_result.document_id)

    assert len(manufacturers) == 1