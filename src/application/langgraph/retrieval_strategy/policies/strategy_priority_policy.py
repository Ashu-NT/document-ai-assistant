from dataclasses import dataclass, field
from functools import lru_cache

from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)
from src.config.paths import PROJECT_ROOT
from src.config.yaml_config_loader import load_yaml_config

_CONFIG_PATH = (
    PROJECT_ROOT / "src" / "config" / "retrieval_strategy" / "strategy_priority.yaml"
)


@lru_cache(maxsize=1)
def _config() -> dict:
    return load_yaml_config(_CONFIG_PATH, description="Retrieval strategy priority")


def _ordered_strategies() -> tuple[RetrievalStrategy, ...]:
    return tuple(
        RetrievalStrategy(name) for name in _config()["ordered_strategies"]
    )


@dataclass(slots=True)
class StrategyPriorityPolicy:
    ordered_strategies: tuple[RetrievalStrategy, ...] = field(
        default_factory=_ordered_strategies
    )

    def sort(self, strategies: list[RetrievalStrategy]) -> list[RetrievalStrategy]:
        rank = {strategy: index for index, strategy in enumerate(self.ordered_strategies)}
        return sorted(strategies, key=lambda item: rank.get(item, len(rank)))
