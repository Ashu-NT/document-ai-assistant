from enum import StrEnum


class IngestionStage(StrEnum):
    DUPLICATE_CHECK = "duplicate_check"
    PARSING = "parsing"
    REGISTRATION = "registration"
    CLASSIFICATION = "classification"
    FINALIZATION = "finalization"
    EXTRACTION = "extraction"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    QUALITY = "quality"
    COMPLETE = "complete"
