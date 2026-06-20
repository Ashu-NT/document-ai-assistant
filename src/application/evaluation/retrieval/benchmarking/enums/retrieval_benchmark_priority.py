from enum import StrEnum


class RetrievalBenchmarkPriority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"

    @classmethod
    def from_value(
        cls,
        value: str,
    ) -> "RetrievalBenchmarkPriority":
        normalized = value.strip().lower().replace(" ", "_").replace("-", "_")

        for member in cls:
            if normalized == member.value:
                return member

        raise ValueError(f"Unsupported retrieval benchmark priority: {value}")
