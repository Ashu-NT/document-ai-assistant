from enum import Enum


class IdPrefix(str, Enum):
    DOCUMENT = "doc"
    SECTION = "sec"
    ELEMENT = "el"
    CHUNK = "chunk"
    QUESTION = "question"
    IDENTIFIER = "identifier"

    INGESTION_RUN = "run"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"

    ACTIVITY = "activity"
    AUDIT = "audit"
    EVENT = "event"

    MEMORY = "memory"
    CONVERSATION = "conversation"
    MESSAGE = "message"

    VECTOR = "vector"