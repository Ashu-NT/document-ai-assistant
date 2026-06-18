from src.domain.memory import (
    ConversationMemory,
    ConversationMessage,
    MemoryEntry,
    SemanticMemoryReference,
)
from src.infrastructure.db.mappers import (
    ConversationMemoryMapper,
    MemoryEntryMapper,
    SemanticMemoryMapper,
)


def test_conversation_memory_mapper_round_trip() -> None:
    memory = ConversationMemory(conversation_id="conv_001")
    memory.add_message(
        ConversationMessage(
            message_id="msg_001",
            role="user",
            content="What are the tasks?",
        )
    )

    memory_orm = ConversationMemoryMapper.memory_to_orm(memory)
    message_rows = [
        ConversationMemoryMapper.message_to_orm(
            memory.messages[0],
            conversation_id=memory.conversation_id,
        )
    ]

    domain = ConversationMemoryMapper.to_domain(memory_orm, message_rows)

    assert domain.conversation_id == "conv_001"
    assert len(domain.messages) == 1
    assert domain.messages[0].content == "What are the tasks?"


def test_memory_entry_mapper_round_trip() -> None:
    entry = MemoryEntry(
        memory_id="memory_001",
        content="User prefers short answers.",
        memory_type="preference",
        importance_score=0.8,
    )

    orm = MemoryEntryMapper.to_orm(entry)
    domain = MemoryEntryMapper.to_domain(orm)

    assert domain.memory_id == entry.memory_id
    assert domain.content == entry.content
    assert domain.memory_type == entry.memory_type


def test_semantic_memory_mapper_round_trip() -> None:
    reference = SemanticMemoryReference(
        reference_id="ref_001",
        source_id="chunk_001",
        source_type="chunk",
        vector_id="vector_001",
        collection_name="document_chunks",
    )

    orm = SemanticMemoryMapper.to_orm(reference)
    domain = SemanticMemoryMapper.to_domain(orm)

    assert domain.reference_id == reference.reference_id
    assert domain.source_id == reference.source_id
    assert domain.vector_id == reference.vector_id