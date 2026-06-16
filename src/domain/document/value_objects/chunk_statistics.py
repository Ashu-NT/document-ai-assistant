from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ChunkStatistics:
    char_count: int
    token_count_estimate: int | None = None

    @classmethod
    def from_text(cls, text: str) -> "ChunkStatistics":
        return cls(
            char_count=len(text),
            token_count_estimate=max(1, len(text.split())),
        )