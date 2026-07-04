from src.application.tools.retrieval.retrieve_structured_entities_tool import (
    RetrieveStructuredEntitiesRequest,
    RetrieveStructuredEntitiesTool,
)
from src.domain.extraction import Manufacturer, Procedure
from src.shared.exceptions import DatabaseError


class _FakeExtractionService:
    def __init__(self) -> None:
        self.search_calls: list[tuple[str, str, str | None]] = []
        self.list_calls: list[tuple[str, str | None]] = []
        self.raises: Exception | None = None

    def search_manufacturers(self, query: str, document_id: str | None = None):
        self.search_calls.append(("manufacturer", query, document_id))
        if self.raises is not None:
            raise self.raises
        return [
            Manufacturer(
                manufacturer_id="manufacturer_001",
                document_id=document_id or "doc_001",
                name="ACME Corp",
                website="https://acme.example",
                source_chunk_id="chunk_001",
            )
        ]

    def list_manufacturers(self, document_id: str | None = None):
        self.list_calls.append(("manufacturer", document_id))
        return [
            Manufacturer(
                manufacturer_id="manufacturer_001",
                document_id=document_id or "doc_001",
                name="ACME Corp",
                source_chunk_id="chunk_001",
            )
        ]

    def search_procedures(self, query: str, document_id: str | None = None):
        self.search_calls.append(("procedure", query, document_id))
        return [
            Procedure(
                procedure_id="procedure_001",
                document_id=document_id or "doc_001",
                title="Install hydraulic filter",
                steps=["Depressurize the line.", "Install the new filter."],
                equipment_id="equipment_001",
                source_chunk_id="chunk_001",
            )
        ]

    def list_procedures(self, document_id: str | None = None):
        self.list_calls.append(("procedure", document_id))
        return [
            Procedure(
                procedure_id="procedure_001",
                document_id=document_id or "doc_001",
                title="Install hydraulic filter",
                equipment_id="equipment_001",
                source_chunk_id="chunk_001",
            )
        ]


def test_retrieve_structured_entities_tool_searches_by_query_text() -> None:
    service = _FakeExtractionService()
    tool = RetrieveStructuredEntitiesTool(service)

    result = tool.run(
        RetrieveStructuredEntitiesRequest(
            entity_type="manufacturer",
            document_id="doc_001",
            query_text="ACME",
        )
    )

    assert result.success is True
    assert service.search_calls == [("manufacturer", "ACME", "doc_001")]
    assert result.data["entity_type"] == "manufacturer"
    assert result.data["items"][0]["name"] == "ACME Corp"
    assert result.data["items"][0]["source_chunk_id"] == "chunk_001"


def test_retrieve_structured_entities_tool_lists_by_document_when_no_query_text() -> None:
    service = _FakeExtractionService()
    tool = RetrieveStructuredEntitiesTool(service)

    result = tool.run(
        RetrieveStructuredEntitiesRequest(
            entity_type="manufacturer",
            document_id="doc_001",
        )
    )

    assert result.success is True
    assert service.list_calls == [("manufacturer", "doc_001")]


def test_retrieve_structured_entities_tool_supports_new_entity_families() -> None:
    service = _FakeExtractionService()
    tool = RetrieveStructuredEntitiesTool(service)

    result = tool.run(
        RetrieveStructuredEntitiesRequest(
            entity_type="procedure",
            document_id="doc_001",
            query_text="hydraulic filter",
        )
    )

    assert result.success is True
    assert service.search_calls == [("procedure", "hydraulic filter", "doc_001")]
    assert result.data["entity_type"] == "procedure"
    assert result.data["items"][0]["title"] == "Install hydraulic filter"
    assert result.data["items"][0]["equipment_id"] == "equipment_001"


def test_retrieve_structured_entities_tool_rejects_unknown_entity_type() -> None:
    service = _FakeExtractionService()
    tool = RetrieveStructuredEntitiesTool(service)

    result = tool.run(
        RetrieveStructuredEntitiesRequest(
            entity_type="not_a_real_type",
            document_id="doc_001",
        )
    )

    assert result.success is False
    assert result.error_code == "invalid_request"


def test_retrieve_structured_entities_tool_requires_document_id_or_query_text() -> None:
    service = _FakeExtractionService()
    tool = RetrieveStructuredEntitiesTool(service)

    result = tool.run(RetrieveStructuredEntitiesRequest(entity_type="manufacturer"))

    assert result.success is False
    assert result.error_code == "invalid_request"


def test_retrieve_structured_entities_tool_truncates_to_top_k() -> None:
    service = _FakeExtractionService()
    tool = RetrieveStructuredEntitiesTool(service)

    result = tool.run(
        RetrieveStructuredEntitiesRequest(
            entity_type="manufacturer",
            document_id="doc_001",
            top_k=0,
        )
    )

    assert result.success is True
    assert result.data["items"] == []
    assert result.diagnostics["total_matches"] == 1


def test_retrieve_structured_entities_tool_wraps_database_errors() -> None:
    service = _FakeExtractionService()
    service.raises = DatabaseError("boom")
    tool = RetrieveStructuredEntitiesTool(service)

    result = tool.run(
        RetrieveStructuredEntitiesRequest(
            entity_type="manufacturer",
            document_id="doc_001",
            query_text="ACME",
        )
    )

    assert result.success is False
    assert result.error_code == "DatabaseError"
