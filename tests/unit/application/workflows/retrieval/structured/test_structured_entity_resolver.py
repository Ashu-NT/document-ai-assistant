from dataclasses import replace

from src.application.workflows.retrieval.structured.structured_entity_resolver import (
    StructuredEntityResolver,
)
from src.application.prompts.extraction.common.extraction_prompt_type import (
    ExtractionPromptType,
)
from src.domain.extraction import (
    SemanticEntityType,
    SemanticRelationship,
    SemanticRelationshipStatus,
    SemanticRelationshipType,
)


class FakeExtractionService:
    def __init__(self) -> None:
        self._search_returns: dict[str, list] = {}
        self._list_returns: dict[str, list] = {}
        self.relationships_by_document: dict[str, list] = {}
        self.calls: list[tuple] = []

    def set_search(self, method_name: str, items: list) -> None:
        self._search_returns[method_name] = items

    def set_list(self, method_name: str, items: list) -> None:
        self._list_returns[method_name] = items

    def __getattr__(self, name: str):
        if name == "list_semantic_relationships":
            def _list_relationships(document_id=None):
                return self.relationships_by_document.get(document_id, [])

            return _list_relationships
        if name.startswith("search_"):
            def _search(query, document_id=None, _name=name):
                self.calls.append((_name, query, document_id))
                return self._search_returns.get(_name, [])

            return _search
        if name.startswith("list_"):
            def _list(document_id=None, _name=name):
                self.calls.append((_name, document_id))
                return self._list_returns.get(_name, [])

            return _list
        raise AttributeError(name)


def test_resolve_uses_search_method_when_query_text_given(sample_manufacturer) -> None:
    service = FakeExtractionService()
    service.set_search("search_manufacturers", [sample_manufacturer])
    resolver = StructuredEntityResolver(service)

    results = resolver.resolve(
        ExtractionPromptType.MANUFACTURER,
        query_text="acme",
        document_id=sample_manufacturer.document_id,
    )

    assert len(results) == 1
    assert results[0]["manufacturer_id"] == sample_manufacturer.manufacturer_id
    assert results[0]["related_entities"] == []
    assert service.calls[0] == (
        "search_manufacturers",
        "acme",
        sample_manufacturer.document_id,
    )


def test_resolve_falls_back_to_list_when_search_returns_nothing(
    sample_manufacturer,
) -> None:
    service = FakeExtractionService()
    service.set_search("search_manufacturers", [])
    service.set_list("list_manufacturers", [sample_manufacturer])
    resolver = StructuredEntityResolver(service)

    results = resolver.resolve(
        ExtractionPromptType.MANUFACTURER,
        query_text="acme",
        document_id=sample_manufacturer.document_id,
        fallback_to_list=True,
    )

    assert len(results) == 1
    assert ("list_manufacturers", sample_manufacturer.document_id) in service.calls


def test_resolve_does_not_fall_back_when_fallback_disabled(sample_manufacturer) -> None:
    service = FakeExtractionService()
    service.set_search("search_manufacturers", [])
    service.set_list("list_manufacturers", [sample_manufacturer])
    resolver = StructuredEntityResolver(service)

    results = resolver.resolve(
        ExtractionPromptType.MANUFACTURER,
        query_text="acme",
        document_id=sample_manufacturer.document_id,
        fallback_to_list=False,
    )

    assert results == []
    assert not any(call[0] == "list_manufacturers" for call in service.calls)


def test_resolve_without_query_text_uses_list_method_directly(
    sample_manufacturer,
) -> None:
    service = FakeExtractionService()
    service.set_list("list_manufacturers", [sample_manufacturer])
    resolver = StructuredEntityResolver(service)

    results = resolver.resolve(
        ExtractionPromptType.MANUFACTURER,
        document_id=sample_manufacturer.document_id,
    )

    assert len(results) == 1


def test_resolve_truncates_to_top_k(sample_manufacturer) -> None:
    other = replace(sample_manufacturer, manufacturer_id="manufacturer_002")
    service = FakeExtractionService()
    service.set_list("list_manufacturers", [sample_manufacturer, other])
    resolver = StructuredEntityResolver(service)

    results = resolver.resolve(
        ExtractionPromptType.MANUFACTURER,
        document_id=sample_manufacturer.document_id,
        top_k=1,
    )

    assert len(results) == 1


def test_entity_id_field_returns_configured_field() -> None:
    resolver = StructuredEntityResolver(FakeExtractionService())

    assert resolver.entity_id_field(ExtractionPromptType.SUPPLIER) == "supplier_id"
    assert resolver.entity_id_field(ExtractionPromptType.MANUFACTURER) == "manufacturer_id"


def test_resolve_attaches_related_entities_via_semantic_relationships(
    sample_manufacturer, sample_contact_point
) -> None:
    service = FakeExtractionService()
    service.set_list("list_manufacturers", [sample_manufacturer])
    service.set_list("list_contact_points", [sample_contact_point])
    service.relationships_by_document[sample_manufacturer.document_id] = [
        SemanticRelationship(
            relationship_id="rel_001",
            document_id=sample_manufacturer.document_id,
            relationship_type=SemanticRelationshipType.MANUFACTURER_HAS_CONTACT_POINT,
            source_entity_type=SemanticEntityType.MANUFACTURER,
            source_entity_id=sample_manufacturer.manufacturer_id,
            target_entity_type=SemanticEntityType.CONTACT_POINT,
            target_entity_id=sample_contact_point.contact_point_id,
            confidence_score=0.9,
            status=SemanticRelationshipStatus.ACCEPTED,
        )
    ]
    resolver = StructuredEntityResolver(service)

    results = resolver.resolve(
        ExtractionPromptType.MANUFACTURER,
        document_id=sample_manufacturer.document_id,
    )

    related_entities = results[0]["related_entities"]
    assert len(related_entities) == 1
    related = related_entities[0]
    assert related["direction"] == "outgoing"
    assert related["entity_type"] == ExtractionPromptType.CONTACT_POINT.value
    assert related["entity_id"] == sample_contact_point.contact_point_id
    assert related["entity"]["contact_point_id"] == sample_contact_point.contact_point_id
