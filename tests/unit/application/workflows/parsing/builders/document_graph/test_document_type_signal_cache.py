from src.application.workflows.parsing.builders.document_graph.document_metadata.document_type_signal_cache import (
    load_document_type_confirmed,
    store_document_type_confirmed,
)


def test_store_then_load_round_trips_true() -> None:
    metadata: dict = {}
    store_document_type_confirmed(metadata, is_confirmed=True)

    assert load_document_type_confirmed(metadata) is True


def test_store_then_load_round_trips_false() -> None:
    metadata: dict = {}
    store_document_type_confirmed(metadata, is_confirmed=False)

    assert load_document_type_confirmed(metadata) is False


def test_missing_key_defaults_to_confirmed_for_pre_existing_documents() -> None:
    # Documents persisted before this cache existed have no recorded
    # provenance -- treat them as confirmed so their existing chunking
    # behavior isn't silently changed by this later code deployment.
    assert load_document_type_confirmed({}) is True
