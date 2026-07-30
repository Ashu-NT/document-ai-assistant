from src.application.services.document import DuplicateDetectionService
from src.shared.activity import ActivityContext


class FakeDocumentRepository:
    def __init__(self) -> None:
        self.file_hash_matches = {}
        self.content_hash_matches = {}
        self.parser_versions = {}

    def find_document_id_by_file_hash(self, file_hash: str) -> str | None:
        return self.file_hash_matches.get(file_hash)

    def find_document_id_by_content_hash(self, content_hash: str) -> str | None:
        return self.content_hash_matches.get(content_hash)

    def find_parser_version_by_document_id(self, document_id: str) -> str | None:
        return self.parser_versions.get(document_id)


def test_check_file_hash_detects_duplicate() -> None:
    repository = FakeDocumentRepository()
    repository.file_hash_matches["hash_001"] = "doc_001"

    service = DuplicateDetectionService(repository)

    result = service.check_file_hash(
        "hash_001",
        activity_context=ActivityContext(actor_id="user_001"),
    )

    assert result.payload["is_duplicate"] is True
    assert result.payload["duplicate_type"] == "file_hash"
    assert result.payload["existing_document_id"] == "doc_001"


def test_check_file_hash_no_duplicate() -> None:
    repository = FakeDocumentRepository()
    service = DuplicateDetectionService(repository)

    result = service.check_file_hash("missing_hash")

    assert result.payload["is_duplicate"] is False
    assert result.payload["existing_document_id"] is None


def test_check_file_hash_treats_stale_parser_version_as_not_duplicate() -> None:
    repository = FakeDocumentRepository()
    repository.file_hash_matches["hash_001"] = "doc_001"
    repository.parser_versions["doc_001"] = "docling==1.0.0"

    service = DuplicateDetectionService(repository)

    result = service.check_file_hash(
        "hash_001",
        current_parser_version="docling==2.0.0",
    )

    assert result.payload["is_duplicate"] is False
    assert result.payload["existing_document_id"] is None
    assert result.payload["stale_document_id"] == "doc_001"


def test_check_content_hash_detects_duplicate() -> None:
    repository = FakeDocumentRepository()
    repository.content_hash_matches["content_hash_001"] = "doc_001"

    service = DuplicateDetectionService(repository)

    result = service.check_content_hash("content_hash_001")

    assert result.payload["is_duplicate"] is True
    assert result.payload["duplicate_type"] == "content_hash"


def test_check_content_hash_treats_stale_parser_version_as_not_duplicate() -> None:
    repository = FakeDocumentRepository()
    repository.content_hash_matches["content_hash_001"] = "doc_001"
    repository.parser_versions["doc_001"] = "docling==1.0.0"

    service = DuplicateDetectionService(repository)

    result = service.check_content_hash(
        "content_hash_001",
        current_parser_version="docling==2.0.0",
    )

    assert result.payload["is_duplicate"] is False
    assert result.payload["existing_document_id"] is None
    assert result.payload["stale_document_id"] == "doc_001"


def test_check_content_hash_still_duplicate_when_parser_version_matches() -> None:
    repository = FakeDocumentRepository()
    repository.content_hash_matches["content_hash_001"] = "doc_001"
    repository.parser_versions["doc_001"] = "docling==2.0.0"

    service = DuplicateDetectionService(repository)

    result = service.check_content_hash(
        "content_hash_001",
        current_parser_version="docling==2.0.0",
    )

    assert result.payload["is_duplicate"] is True
    assert result.payload["existing_document_id"] == "doc_001"


def test_check_content_hash_skips_version_check_when_not_provided() -> None:
    repository = FakeDocumentRepository()
    repository.content_hash_matches["content_hash_001"] = "doc_001"

    service = DuplicateDetectionService(repository)

    result = service.check_content_hash("content_hash_001")

    assert result.payload["is_duplicate"] is True
    assert result.payload["existing_document_id"] == "doc_001"