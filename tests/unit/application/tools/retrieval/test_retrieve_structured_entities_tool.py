from src.application.tools.retrieval.retrieve_structured_entities_tool import (
    RetrieveStructuredEntitiesRequest,
    RetrieveStructuredEntitiesTool,
)
from src.domain.extraction import (
    ContactPoint,
    ContactPointType,
    Manufacturer,
    MaintenanceTask,
    Procedure,
    SafetyWarning,
    SemanticEntityType,
    SemanticRelationship,
    SemanticRelationshipStatus,
    SemanticRelationshipType,
    SparePart,
)
from src.shared.exceptions import DatabaseError


class _FakeExtractionService:
    def __init__(self) -> None:
        self.search_calls: list[tuple[str, str, str | None]] = []
        self.list_calls: list[tuple[str, str | None]] = []
        self.raises: Exception | None = None
        self.semantic_relationships: dict[str, list[SemanticRelationship]] = {}
        self.list_semantic_relationships_calls: list[str | None] = []

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

    def search_contact_points(self, query: str, document_id: str | None = None):
        self.search_calls.append(("contact_point", query, document_id))
        return [
            ContactPoint(
                contact_point_id="contact_point_001",
                document_id=document_id or "doc_001",
                contact_type=ContactPointType.EMAIL_ADDRESS,
                value="service@acme.example",
                owner_name="ACME Corp",
                owner_entity_type=SemanticEntityType.MANUFACTURER,
                source_chunk_id="chunk_contact_001",
            )
        ]

    def list_contact_points(self, document_id: str | None = None):
        self.list_calls.append(("contact_point", document_id))
        return [
            ContactPoint(
                contact_point_id="contact_point_001",
                document_id=document_id or "doc_001",
                contact_type=ContactPointType.EMAIL_ADDRESS,
                value="service@acme.example",
                owner_name="ACME Corp",
                owner_entity_type=SemanticEntityType.MANUFACTURER,
                source_chunk_id="chunk_contact_001",
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

    def list_maintenance_tasks(self, document_id: str | None = None):
        self.list_calls.append(("maintenance_task", document_id))
        return [
            MaintenanceTask(
                task_id="task_001",
                document_id=document_id or "doc_001",
                title="Replace hydraulic filter",
            )
        ]

    def list_spare_parts(self, document_id: str | None = None):
        self.list_calls.append(("spare_part", document_id))
        return [
            SparePart(
                spare_part_id="spare_001",
                document_id=document_id or "doc_001",
                part_number="HP-001",
            )
        ]

    def list_safety_warnings(self, document_id: str | None = None):
        self.list_calls.append(("safety_warning", document_id))
        return [
            SafetyWarning(
                safety_warning_id="warning_001",
                document_id=document_id or "doc_001",
                warning_type="hazard",
                message="Depressurize before servicing",
            )
        ]

    def list_semantic_relationships(self, document_id: str | None = None):
        self.list_semantic_relationships_calls.append(document_id)
        if document_id is None:
            return [
                relationship
                for relationships in self.semantic_relationships.values()
                for relationship in relationships
            ]
        return self.semantic_relationships.get(document_id, [])


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


def test_retrieve_structured_entities_tool_supports_contact_points() -> None:
    service = _FakeExtractionService()
    tool = RetrieveStructuredEntitiesTool(service)

    result = tool.run(
        RetrieveStructuredEntitiesRequest(
            entity_type="contact_point",
            document_id="doc_001",
            query_text="service@acme.example",
        )
    )

    assert result.success is True
    assert service.search_calls == [("contact_point", "service@acme.example", "doc_001")]
    assert result.data["items"][0]["value"] == "service@acme.example"
    assert result.data["items"][0]["owner_name"] == "ACME Corp"


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


def _relationship(**overrides) -> SemanticRelationship:
    defaults = {
        "relationship_id": "semantic_relationship_001",
        "document_id": "doc_001",
        "relationship_type": SemanticRelationshipType.TASK_USES_PROCEDURE,
        "source_entity_type": SemanticEntityType.MAINTENANCE_TASK,
        "source_entity_id": "task_001",
        "target_entity_type": SemanticEntityType.PROCEDURE,
        "target_entity_id": "procedure_001",
        "confidence_score": 0.8,
        "status": SemanticRelationshipStatus.ACCEPTED,
        "evidence": "same_chunk",
    }
    defaults.update(overrides)
    return SemanticRelationship(**defaults)


def test_retrieve_structured_entities_tool_attaches_outgoing_related_entity() -> None:
    service = _FakeExtractionService()
    service.semantic_relationships["doc_001"] = [_relationship()]
    tool = RetrieveStructuredEntitiesTool(service)

    result = tool.run(
        RetrieveStructuredEntitiesRequest(
            entity_type="maintenance_task",
            document_id="doc_001",
        )
    )

    assert result.success is True
    related = result.data["items"][0]["related_entities"]
    assert len(related) == 1
    assert related[0]["relationship_type"] == "task_uses_procedure"
    assert related[0]["direction"] == "outgoing"
    assert related[0]["status"] == "accepted"
    assert related[0]["entity_type"] == "procedure"
    assert related[0]["entity_id"] == "procedure_001"
    assert related[0]["entity"]["title"] == "Install hydraulic filter"
    assert service.list_semantic_relationships_calls == ["doc_001"]


def test_retrieve_structured_entities_tool_attaches_incoming_related_entity() -> None:
    service = _FakeExtractionService()
    service.semantic_relationships["doc_001"] = [_relationship()]
    tool = RetrieveStructuredEntitiesTool(service)

    result = tool.run(
        RetrieveStructuredEntitiesRequest(
            entity_type="procedure",
            document_id="doc_001",
        )
    )

    assert result.success is True
    related = result.data["items"][0]["related_entities"]
    assert len(related) == 1
    assert related[0]["direction"] == "incoming"
    assert related[0]["entity_type"] == "maintenance_task"
    assert related[0]["entity_id"] == "task_001"
    assert related[0]["entity"]["title"] == "Replace hydraulic filter"


def test_retrieve_structured_entities_tool_aggregates_multiple_relationship_types() -> None:
    service = _FakeExtractionService()
    service.semantic_relationships["doc_001"] = [
        _relationship(),
        _relationship(
            relationship_id="semantic_relationship_002",
            relationship_type=SemanticRelationshipType.TASK_REQUIRES_SPARE_PART,
            target_entity_type=SemanticEntityType.SPARE_PART,
            target_entity_id="spare_001",
        ),
        _relationship(
            relationship_id="semantic_relationship_003",
            relationship_type=SemanticRelationshipType.TASK_REQUIRES_SAFETY_WARNING,
            target_entity_type=SemanticEntityType.SAFETY_WARNING,
            target_entity_id="warning_001",
            status=SemanticRelationshipStatus.NEEDS_REVIEW,
        ),
    ]
    tool = RetrieveStructuredEntitiesTool(service)

    result = tool.run(
        RetrieveStructuredEntitiesRequest(
            entity_type="maintenance_task",
            document_id="doc_001",
        )
    )

    related = result.data["items"][0]["related_entities"]
    relationship_types = {entry["relationship_type"] for entry in related}
    assert relationship_types == {
        "task_uses_procedure",
        "task_requires_spare_part",
        "task_requires_safety_warning",
    }
    spare_part_entry = next(
        entry for entry in related if entry["entity_type"] == "spare_part"
    )
    assert spare_part_entry["entity"]["part_number"] == "HP-001"
    warning_entry = next(
        entry for entry in related if entry["entity_type"] == "safety_warning"
    )
    assert warning_entry["status"] == "needs_review"


def test_retrieve_structured_entities_tool_returns_empty_related_entities_by_default() -> (
    None
):
    service = _FakeExtractionService()
    tool = RetrieveStructuredEntitiesTool(service)

    result = tool.run(
        RetrieveStructuredEntitiesRequest(
            entity_type="manufacturer",
            document_id="doc_001",
        )
    )

    assert result.data["items"][0]["related_entities"] == []


def test_retrieve_structured_entities_tool_attaches_contact_point_related_entity() -> None:
    service = _FakeExtractionService()
    service.semantic_relationships["doc_001"] = [
        _relationship(
            relationship_type=SemanticRelationshipType.MANUFACTURER_HAS_CONTACT_POINT,
            source_entity_type=SemanticEntityType.MANUFACTURER,
            source_entity_id="manufacturer_001",
            target_entity_type=SemanticEntityType.CONTACT_POINT,
            target_entity_id="contact_point_001",
        )
    ]
    tool = RetrieveStructuredEntitiesTool(service)

    result = tool.run(
        RetrieveStructuredEntitiesRequest(
            entity_type="manufacturer",
            document_id="doc_001",
        )
    )

    assert result.success is True
    related = result.data["items"][0]["related_entities"]
    assert len(related) == 1
    assert related[0]["entity_type"] == "contact_point"
    assert related[0]["entity"]["value"] == "service@acme.example"


def test_retrieve_structured_entities_tool_skips_enrichment_when_relationships_lookup_fails() -> (
    None
):
    service = _FakeExtractionService()
    service.semantic_relationships["doc_001"] = [_relationship()]

    def _raise(document_id):
        raise DatabaseError("boom")

    service.list_semantic_relationships = _raise
    tool = RetrieveStructuredEntitiesTool(service)

    result = tool.run(
        RetrieveStructuredEntitiesRequest(
            entity_type="maintenance_task",
            document_id="doc_001",
        )
    )

    assert result.success is True
    assert result.data["items"][0]["related_entities"] == []


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
