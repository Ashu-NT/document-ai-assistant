from src.domain.memory import ConversationMemory, ConversationMessage


def test_conversation_memory_adds_message() -> None:
    memory = ConversationMemory(conversation_id="conv_001")

    memory.add_message(
        ConversationMessage(
            message_id="msg_001",
            role="user",
            content="What are the tasks?",
        )
    )

    assert not memory.is_empty()
    assert len(memory.messages) == 1


def test_conversation_memory_returns_latest_messages() -> None:
    memory = ConversationMemory(conversation_id="conv_001")

    memory.add_message(ConversationMessage("msg_001", "user", "first"))
    memory.add_message(ConversationMessage("msg_002", "assistant", "second"))

    latest = memory.latest_messages(limit=1)

    assert len(latest) == 1
    assert latest[0].content == "second"