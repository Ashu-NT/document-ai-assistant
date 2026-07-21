from src.application.workflows.question_answering.answer_pipeline.structured_evidence_scope import (
    StructuredEvidenceScope,
)
from src.application.workflows.question_answering.answer_pipeline.structured_evidence_scope_filter import (
    StructuredEvidenceScopeFilter,
)
from src.domain.common import ChunkType, IdentifierType
from src.domain.common.source_location import SourceLocation
from src.domain.document.entities.identifier import Identifier
from src.domain.retrieval import RetrievedChunk


def _make_chunk(
    *,
    chunk_id: str = "chunk_approved",
    metadata: dict[str, str] | None = None,
    page_start: int = 89,
    page_end: int = 96,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content="Approved content",
        score=1.0,
        retrieval_source="sql",
        chunk_type=ChunkType.GENERAL,
        source=SourceLocation(page_start=page_start, page_end=page_end),
        metadata=metadata or {},
    )


def test_filter_keeps_entity_grounded_via_collapsed_chunk_id() -> None:
    scope = StructuredEvidenceScope.from_chunks(
        [_make_chunk(metadata={"dedup_collapsed_chunk_ids": "chunk_structured"})]
    )
    filtered = StructuredEvidenceScopeFilter(scope).filter_entities(
        [
            {
                "_entity_type": "troubleshooting",
                "source_chunk_id": "chunk_structured",
                "document_id": "doc_001",
                "symptom": "Pump will not start",
                "related_entities": [
                    {
                        "entity_type": "procedure",
                        "entity": {
                            "source_chunk_id": "chunk_structured",
                            "document_id": "doc_001",
                            "title": "Reset starter",
                        },
                    },
                    {
                        "entity_type": "procedure",
                        "entity": {
                            "source_chunk_id": "chunk_other",
                            "document_id": "doc_001",
                            "title": "Wrong relation",
                        },
                    },
                ],
            }
        ]
    )

    assert len(filtered) == 1
    assert filtered[0]["source_chunk_id"] == "chunk_structured"
    assert len(filtered[0]["related_entities"]) == 1
    assert filtered[0]["related_entities"][0]["entity"]["title"] == "Reset starter"


def test_filter_drops_entity_outside_approved_scope() -> None:
    scope = StructuredEvidenceScope.from_chunks([_make_chunk()])
    filtered = StructuredEvidenceScopeFilter(scope).filter_entities(
        [
            {
                "_entity_type": "troubleshooting",
                "document_id": "doc_001",
                "symptom": "Old issue",
                "source_metadata": {
                    "document_id": "doc_001",
                    "chunk_id": "chunk_page_10",
                    "page_start": 10,
                    "page_end": 11,
                },
            }
        ]
    )

    assert filtered == []


def test_filter_identifiers_uses_chunk_or_page_scope() -> None:
    scope = StructuredEvidenceScope.from_chunks([_make_chunk(page_start=50, page_end=50)])
    identifiers = [
        Identifier(
            identifier_id="id_001",
            document_id="doc_001",
            raw_value="HP-001",
            identifier_type=IdentifierType.PART_NUMBER,
            chunk_id="chunk_approved",
            confidence_score=0.9,
        ),
        Identifier(
            identifier_id="id_002",
            document_id="doc_001",
            raw_value="HP-002",
            identifier_type=IdentifierType.PART_NUMBER,
            page_start=50,
            page_end=50,
            confidence_score=0.9,
        ),
        Identifier(
            identifier_id="id_003",
            document_id="doc_001",
            raw_value="HP-003",
            identifier_type=IdentifierType.PART_NUMBER,
            page_start=51,
            page_end=51,
            confidence_score=0.9,
        ),
    ]

    filtered = StructuredEvidenceScopeFilter(scope).filter_identifiers(identifiers)

    assert [identifier.raw_value for identifier in filtered] == ["HP-001", "HP-002"]
