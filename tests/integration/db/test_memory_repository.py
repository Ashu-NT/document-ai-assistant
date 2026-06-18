from src.domain.memory import (
    ConversationMemory,
    ConversationMessage,
    MemoryEntry,
    SemanticMemoryReference,
)


def test_save_and_load_conversation_memory(db_uow) -> None:
    memory = ConversationMemory(conversation_id="conv_001")
    memory.add_message(
        ConversationMessage(
            message_id="msg_001",
            role="user",
            content="What maintenance tasks exist?",
        )
    )

    db_uow.memory.save_conversation_memory(memory)
    db_uow.commit()

    loaded = db_uow.memory.get_conversation_memory("conv_001")

    assert loaded is not None
    assert loaded.conversation_id == "conv_001"
    assert len(loaded.messages) == 1


def test_save_and_search_memory_entry(db_uow) -> None:
    entry = MemoryEntry(
        memory_id="memory_001",
        content="User prefers short technical answers.",
        memory_type="preference",
        importance_score=0.8,
    )

    db_uow.memory.save_memory_entry(entry)
    db_uow.commit()

    results = db_uow.memory.search_memory_entries(
        query="technical answers",
        limit=5,
    )

    assert len(results) == 1
    assert results[0].memory_id == "memory_001"


def test_save_semantic_memory_reference(db_uow) -> None:
    reference = SemanticMemoryReference(
        reference_id="ref_001",
        source_id="chunk_001",
        source_type="chunk",
        vector_id="vector_001",
        collection_name="document_chunks",
    )

    db_uow.memory.save_semantic_reference(reference)
    db_uow.commit()

    # No get method yet, so this only verifies save + commit does not fail.