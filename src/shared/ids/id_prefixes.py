

from sqlalchemy import Enum


class IdPrefix(str, Enum):
    DOCUMENT = "doc"
    SECTION = "sec"
    ELEMENT = "el"
    CHUNK = "chunk"
    QUESTION = "question"
    IDENTIFIER = "identifier"
    CROSS_REFERENCE = "xref"
    CROSS_REFERENCE_EVIDENCE = "xref_evidence"

    INGESTION_RUN = "run"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"

    ACTIVITY = "activity"
    AUDIT = "audit"
    EVENT = "event"
    RETRIEVAL = "retrieval"

    MEMORY = "memory"
    CONVERSATION = "conversation"
    MESSAGE = "message"

    VECTOR = "vector"