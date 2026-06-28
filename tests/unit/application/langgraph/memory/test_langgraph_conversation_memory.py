from src.application.langgraph.memory import ConversationMemory


def test_conversation_memory_caps_history() -> None:
    memory = ConversationMemory(max_messages=2)

    memory.append_user_message("one")
    memory.append_assistant_message("two")
    memory.append_user_message("three")

    history = memory.get_history()
    assert len(history) == 2
    assert history[0]["content"] == "two"
    assert history[1]["content"] == "three"
