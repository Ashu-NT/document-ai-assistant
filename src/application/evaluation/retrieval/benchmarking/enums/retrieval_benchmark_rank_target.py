from enum import StrEnum


class RetrievalBenchmarkRankTarget(StrEnum):
    TOP_1 = "top_1"
    TOP_3 = "top_3"
    TOP_5 = "top_5"
    TOP_10 = "top_10"

    @classmethod
    def from_value(
        cls,
        value: str,
    ) -> "RetrievalBenchmarkRankTarget":
        normalized = value.strip().lower().replace(" ", "_").replace("-", "_")

        for member in cls:
            if normalized == member.value:
                return member

        raise ValueError(f"Unsupported retrieval benchmark rank target: {value}")
