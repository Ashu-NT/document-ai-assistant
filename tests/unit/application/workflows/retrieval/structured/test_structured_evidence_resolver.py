import pytest

from src.application.prompts.extraction.common.extraction_prompt_type import (
    ExtractionPromptType,
)
from src.application.workflows.retrieval.structured.structured_evidence_query_analysis import (
    StructuredEvidenceQueryAnalysis,
)
from src.application.workflows.retrieval.structured.structured_evidence_resolver import (
    StructuredEvidenceResolver,
)
from src.domain.common import IdentifierType
from src.domain.document.entities.identifier import Identifier
from src.domain.retrieval import RetrievalQuery


class FakeDocumentLookupService:
    def __init__(
        self,
        *,
        identifiers_by_type: dict | None = None,
        identifiers_by_value: dict | None = None,
        chunks_by_id: dict | None = None,
    ) -> None:
        self.identifiers_by_type = identifiers_by_type or {}
        self.identifiers_by_value = identifiers_by_value or {}
        self.chunks_by_id = chunks_by_id or {}

    def search_identifiers(self, value):
        return self.identifiers_by_value.get(value, [])

    def search_identifiers_by_type(self, identifier_type, document_id):
        return self.identifiers_by_type.get((identifier_type, document_id), [])

    def get_chunks_by_ids(self, chunk_ids):
        return [
            self.chunks_by_id[chunk_id]
            for chunk_id in chunk_ids
            if chunk_id in self.chunks_by_id
        ]


class FakeEntityResolver:
    def __init__(self, *, entities_by_type: dict | None = None) -> None:
        self.entities_by_type = entities_by_type or {}
        self.resolve_calls: list[tuple] = []

    def resolve(
        self,
        entity_type,
        *,
        query_text=None,
        document_id=None,
        top_k=None,
        fallback_to_list=False,
    ):
        self.resolve_calls.append(
            (entity_type, query_text, document_id, top_k, fallback_to_list)
        )
        return self.entities_by_type.get(entity_type, [])

    @staticmethod
    def entity_id_field(entity_type):
        return {
            ExtractionPromptType.MANUFACTURER: "manufacturer_id",
            ExtractionPromptType.SPARE_PART: "spare_part_id",
            ExtractionPromptType.SPECIFICATION: "specification_id",
        }[entity_type]


class FakeQueryAnalyzer:
    def __init__(self, analysis: StructuredEvidenceQueryAnalysis) -> None:
        self.analysis = analysis
        self.calls: list[tuple] = []

    def analyze(self, *, query_text, intent=None, detected_identifiers=None):
        self.calls.append((query_text, intent, detected_identifiers))
        return self.analysis


def test_resolve_combines_identifiers_and_entities_into_scored_chunks(
    sample_chunk, document_id, chunk_id
) -> None:
    identifier = Identifier(
        identifier_id="identifier_001",
        document_id=document_id,
        chunk_id=chunk_id,
        raw_value="HP-001",
        identifier_type=IdentifierType.PART_NUMBER,
    )
    entity = {
        "manufacturer_id": "manufacturer_001",
        "source_chunk_id": chunk_id,
        "_entity_type": ExtractionPromptType.MANUFACTURER.value,
        "related_entities": [],
    }
    document_lookup_service = FakeDocumentLookupService(
        identifiers_by_type={
            (IdentifierType.PART_NUMBER.value, document_id): [identifier]
        },
        chunks_by_id={chunk_id: sample_chunk},
    )
    entity_resolver = FakeEntityResolver(
        entities_by_type={ExtractionPromptType.MANUFACTURER: [entity]},
    )
    resolver = StructuredEvidenceResolver(
        document_lookup_service=document_lookup_service,
        entity_resolver=entity_resolver,
        query_analyzer=FakeQueryAnalyzer(
            StructuredEvidenceQueryAnalysis(
                entity_types=[ExtractionPromptType.MANUFACTURER],
                identifier_types=[IdentifierType.PART_NUMBER],
            )
        ),
    )
    query = RetrievalQuery(
        query_id="query_001",
        query_text="Who is the manufacturer of part HP-001?",
        document_id=document_id,
    )

    bundle = resolver.resolve(query)

    assert bundle.has_results()
    assert len(bundle.chunks) == 1
    chunk = bundle.chunks[0]
    assert chunk.retrieval_source == "structured"
    assert chunk.score == pytest.approx(1.0 + 0.95)
    assert chunk.metadata["structured_match_count"] == "2"
    assert "identifier:part_number" in chunk.metadata["structured_match_reasons"]
    assert "entity:manufacturer" in chunk.metadata["structured_match_reasons"]
    assert chunk.metadata["structured_identifier_types"] == "part_number"
    assert chunk.metadata["structured_entity_types"] == "manufacturer"
    assert bundle.diagnostics["structured_identifier_count"] == 1
    assert bundle.diagnostics["structured_entity_count"] == 1
    assert bundle.diagnostics["structured_chunk_count"] == 1


def test_resolve_returns_empty_bundle_when_nothing_matches(document_id) -> None:
    resolver = StructuredEvidenceResolver(
        document_lookup_service=FakeDocumentLookupService(),
        entity_resolver=FakeEntityResolver(),
        query_analyzer=FakeQueryAnalyzer(StructuredEvidenceQueryAnalysis()),
    )
    query = RetrievalQuery(
        query_id="query_002",
        query_text="hello",
        document_id=document_id,
    )

    bundle = resolver.resolve(query)

    assert not bundle.has_results()
    assert bundle.chunks == []
    assert bundle.diagnostics["structured_identifier_count"] == 0
    assert bundle.diagnostics["structured_entity_count"] == 0


def test_resolve_deduplicates_identifiers_with_same_normalized_value(
    document_id, chunk_id, sample_chunk
) -> None:
    identifier_a = Identifier(
        identifier_id="identifier_a",
        document_id=document_id,
        chunk_id=chunk_id,
        raw_value="HP-001",
        identifier_type=IdentifierType.PART_NUMBER,
    )
    identifier_b = Identifier(
        identifier_id="identifier_b",
        document_id=document_id,
        chunk_id=chunk_id,
        raw_value="hp-001",
        identifier_type=IdentifierType.PART_NUMBER,
    )
    document_lookup_service = FakeDocumentLookupService(
        identifiers_by_type={
            (IdentifierType.PART_NUMBER.value, document_id): [
                identifier_a,
                identifier_b,
            ]
        },
        chunks_by_id={chunk_id: sample_chunk},
    )
    resolver = StructuredEvidenceResolver(
        document_lookup_service=document_lookup_service,
        entity_resolver=FakeEntityResolver(),
        query_analyzer=FakeQueryAnalyzer(
            StructuredEvidenceQueryAnalysis(identifier_types=[IdentifierType.PART_NUMBER])
        ),
    )
    query = RetrievalQuery(
        query_id="query_003",
        query_text="part HP-001",
        document_id=document_id,
    )

    bundle = resolver.resolve(query)

    assert len(bundle.identifiers) == 1


def test_resolve_enables_fallback_to_list_for_spare_part_and_specification(
    document_id,
) -> None:
    entity_resolver = FakeEntityResolver()
    resolver = StructuredEvidenceResolver(
        document_lookup_service=FakeDocumentLookupService(),
        entity_resolver=entity_resolver,
        query_analyzer=FakeQueryAnalyzer(
            StructuredEvidenceQueryAnalysis(
                entity_types=[
                    ExtractionPromptType.SPARE_PART,
                    ExtractionPromptType.SPECIFICATION,
                ]
            )
        ),
    )
    query = RetrievalQuery(
        query_id="query_004",
        query_text="list the spare parts",
        document_id=document_id,
    )

    resolver.resolve(query)

    fallback_flags = {
        entity_type: fallback_to_list
        for entity_type, _, _, _, fallback_to_list in entity_resolver.resolve_calls
    }
    assert fallback_flags[ExtractionPromptType.SPARE_PART] is True
    assert fallback_flags[ExtractionPromptType.SPECIFICATION] is True


def test_resolve_does_not_enable_fallback_to_list_without_document_id() -> None:
    entity_resolver = FakeEntityResolver()
    resolver = StructuredEvidenceResolver(
        document_lookup_service=FakeDocumentLookupService(),
        entity_resolver=entity_resolver,
        query_analyzer=FakeQueryAnalyzer(
            StructuredEvidenceQueryAnalysis(
                entity_types=[ExtractionPromptType.SPARE_PART]
            )
        ),
    )
    query = RetrievalQuery(
        query_id="query_005",
        query_text="list the spare parts",
        document_id=None,
    )

    resolver.resolve(query)

    _, _, _, _, fallback_to_list = entity_resolver.resolve_calls[0]
    assert fallback_to_list is False


def test_resolve_detail_entities_returns_empty_when_no_detail_entity_type() -> None:
    resolver = StructuredEvidenceResolver(
        document_lookup_service=FakeDocumentLookupService(),
        entity_resolver=FakeEntityResolver(),
        query_analyzer=FakeQueryAnalyzer(
            StructuredEvidenceQueryAnalysis(detail_entity_type=None)
        ),
    )

    results = resolver.resolve_detail_entities(
        query_text="hello",
        document_id="doc_001",
    )

    assert results == []


def test_resolve_detail_entities_delegates_to_entity_resolver_when_present() -> None:
    entity_resolver = FakeEntityResolver(
        entities_by_type={
            ExtractionPromptType.MANUFACTURER: [{"manufacturer_id": "manufacturer_001"}]
        }
    )
    resolver = StructuredEvidenceResolver(
        document_lookup_service=FakeDocumentLookupService(),
        entity_resolver=entity_resolver,
        query_analyzer=FakeQueryAnalyzer(
            StructuredEvidenceQueryAnalysis(
                detail_entity_type=ExtractionPromptType.MANUFACTURER
            )
        ),
    )

    results = resolver.resolve_detail_entities(
        query_text="who is the manufacturer's email",
        document_id="doc_001",
        top_k=5,
    )

    assert results == [{"manufacturer_id": "manufacturer_001"}]
    entity_type, query_text, document_id, top_k, _ = entity_resolver.resolve_calls[0]
    assert entity_type == ExtractionPromptType.MANUFACTURER
    assert query_text == "who is the manufacturer's email"
    assert document_id == "doc_001"
    assert top_k == 5
