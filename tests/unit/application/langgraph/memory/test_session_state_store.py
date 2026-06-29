from src.application.langgraph.memory import SessionStateStore


def test_session_state_store_saves_and_loads_state() -> None:
    store = SessionStateStore(persist_to_disk=False)

    store.save(
        "demo",
        {
            "selected_document_id": "doc-42",
            "selected_document_title": "FWC12 Manual",
        },
    )

    loaded = store.get("demo")

    assert loaded == {
        "selected_document_id": "doc-42",
        "selected_document_title": "FWC12 Manual",
    }


def test_session_state_store_clears_state() -> None:
    store = SessionStateStore(persist_to_disk=False)
    store.save("demo", {"selected_document_id": "doc-42"})

    store.clear("demo")

    assert store.get("demo") is None
