from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RetrievalStrategySignal:
    category: str
    value: str
    score: float = 1.0
