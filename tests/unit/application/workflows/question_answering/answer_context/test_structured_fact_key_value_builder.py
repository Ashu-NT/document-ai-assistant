from src.application.workflows.question_answering.answer_context.structured_fact_key_value_builder import (
    StructuredFactKeyValueBuilder,
)
from src.domain.common.enums import IdentifierType
from src.domain.document.entities.identifier import Identifier


def test_build_from_identifiers_skips_identifiers_without_a_mapped_source_chunk() -> None:
    builder = StructuredFactKeyValueBuilder()
    identifier = Identifier(
        identifier_id="id_1",
        document_id="doc_1",
        raw_value="HP-001",
        identifier_type=IdentifierType.PART_NUMBER,
        chunk_id="chunk_not_mapped",
    )

    key_values = builder.build_from_identifiers(
        [identifier], source_number_by_chunk_id={}
    )

    assert key_values == []


def test_build_from_identifiers_produces_titled_key_and_source_number() -> None:
    builder = StructuredFactKeyValueBuilder()
    identifier = Identifier(
        identifier_id="id_1",
        document_id="doc_1",
        raw_value="HP-001",
        identifier_type=IdentifierType.PART_NUMBER,
        chunk_id="chunk_1",
        confidence_score=0.9,
    )

    key_values = builder.build_from_identifiers(
        [identifier], source_number_by_chunk_id={"chunk_1": 3}
    )

    assert len(key_values) == 1
    assert key_values[0].key == "Part Number"
    assert key_values[0].value == "HP-001"
    assert key_values[0].source_number == 3
    assert key_values[0].confidence == 0.9


def test_build_from_structured_entities_maps_known_fields_for_manufacturer() -> None:
    builder = StructuredFactKeyValueBuilder()
    entity = {
        "name": "ACME Corp",
        "website": "https://acme.example",
        "country": None,
        "source_chunk_id": "chunk_1",
        "confidence_score": 0.85,
    }

    key_values = builder.build_from_structured_entities(
        "manufacturer", [entity], source_number_by_chunk_id={"chunk_1": 1}
    )

    pairs = {(kv.key, kv.value) for kv in key_values}
    assert ("Manufacturer Name", "ACME Corp") in pairs
    assert ("Manufacturer Website", "https://acme.example") in pairs
    assert not any(kv.key == "Manufacturer Country" for kv in key_values)


def test_build_from_structured_entities_skips_entities_without_a_mapped_source_chunk() -> None:
    builder = StructuredFactKeyValueBuilder()
    entity = {"name": "ACME Corp", "source_chunk_id": "chunk_unmapped"}

    key_values = builder.build_from_structured_entities(
        "manufacturer", [entity], source_number_by_chunk_id={}
    )

    assert key_values == []


def test_build_from_structured_entities_ignores_unknown_entity_type() -> None:
    builder = StructuredFactKeyValueBuilder()
    entity = {"name": "ACME Corp", "source_chunk_id": "chunk_1"}

    key_values = builder.build_from_structured_entities(
        "unknown_entity_type", [entity], source_number_by_chunk_id={"chunk_1": 1}
    )

    assert key_values == []


def test_build_from_structured_entities_includes_related_contact_points() -> None:
    builder = StructuredFactKeyValueBuilder()
    entity = {
        "name": "ACME Corp",
        "source_chunk_id": "chunk_manufacturer",
        "related_entities": [
            {
                "entity_type": "contact_point",
                "entity": {
                    "contact_type": "email_address",
                    "value": "service@acme.example",
                    "owner_name": "ACME Corp",
                    "owner_entity_type": "manufacturer",
                    "source_chunk_id": "chunk_contact",
                },
            }
        ],
    }

    key_values = builder.build_from_structured_entities(
        "manufacturer",
        [entity],
        source_number_by_chunk_id={
            "chunk_manufacturer": 1,
            "chunk_contact": 2,
        },
    )

    pairs = {(kv.key, kv.value, kv.source_number) for kv in key_values}
    assert ("Manufacturer Name", "ACME Corp", 1) in pairs
    assert ("Manufacturer Email Address", "service@acme.example", 2) in pairs
