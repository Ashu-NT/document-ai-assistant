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
