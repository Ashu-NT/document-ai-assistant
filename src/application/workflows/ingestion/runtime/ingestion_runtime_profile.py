from enum import StrEnum


class IngestionRuntimeProfile(StrEnum):
    AUTO = "auto"
    STRUCTURAL_ONLY = "structural_only"
    SEMANTIC_ENRICHED = "semantic_enriched"
