from src.application.langgraph.memory import ConversationMemory, SessionStateStore


def test_conversation_memory_caps_history() -> None:
    memory = ConversationMemory(max_messages=2)

    memory.append_user_message("one")
    memory.append_assistant_message("two")
    memory.append_user_message("three")

    history = memory.get_history()
    assert len(history) == 2
    assert history[0]["content"] == "two"
    assert history[1]["content"] == "three"


def test_conversation_memory_loads_and_saves_session_state() -> None:
    store = SessionStateStore(persist_to_disk=False)
    memory = ConversationMemory(max_messages=3, session_state_store=store)

    memory.load_session("demo")
    memory.append_user_message("open FWC12", conversation_id="demo")
    memory.save_session_state(
        session_id="demo",
        selected_document_id="doc-42",
        selected_document_title="FWC12 Manual",
        selected_document_file_name="fwc12.pdf",
        pending_clarification=None,
        clarification_options=[],
        clarification_question=None,
    )

    reloaded = ConversationMemory(max_messages=3, session_state_store=store)
    snapshot = reloaded.load_session("demo")

    assert snapshot["selected_document_id"] == "doc-42"
    assert snapshot["selected_document_title"] == "FWC12 Manual"
    assert snapshot["history"][0]["content"] == "open FWC12"
