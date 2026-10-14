from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(slots=True)
class ExtractionExecutionBudget:
    deadline: float | None
    clock: Callable[[], float]
    total_seconds: float | None = None

    @classmethod
    def start(
        cls,
        budget_seconds: float | None,
        *,
        clock: Callable[[], float] | None = None,
    ) -> ExtractionExecutionBudget:
        resolved_clock = clock or time.monotonic
        deadline = (
            resolved_clock() + budget_seconds if budget_seconds is not None else None
        )
        return cls(deadline=deadline, clock=resolved_clock, total_seconds=budget_seconds)

    def is_expired(self) -> bool:
        return self.deadline is not None and self.clock() >= self.deadline

    def remaining_seconds(self) -> float | None:
        if self.deadline is None:
            return None
        return max(0.0, self.deadline - self.clock())

    def elapsed_seconds(self) -> float | None:
        if self.total_seconds is None:
            return None
        remaining = self.remaining_seconds()
        return None if remaining is None else max(0.0, self.total_seconds - remaining)


def describe_budget_exhaustion(budget: ExtractionExecutionBudget) -> str:
    elapsed = budget.elapsed_seconds()
    return (
        f"execution budget exhausted after {elapsed:.1f}s"
        if elapsed is not None
        else "execution budget exhausted"
    )
