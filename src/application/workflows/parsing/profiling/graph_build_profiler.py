from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter
from typing import Iterator

from src.application.workflows.parsing.profiling.graph_build_stage_models import (
    GraphBuildStageMetric,
    GraphBuildStageScope,
)


class GraphBuildProfiler:
    def __init__(
        self,
        *,
        enabled: bool = True,
        progress_callback=None,
    ) -> None:
        self.enabled = enabled
        self.progress_callback = progress_callback
        self.stage_metrics: list[GraphBuildStageMetric] = []
        self._started_at: float | None = None

    @classmethod
    def disabled(cls) -> "GraphBuildProfiler":
        return cls(enabled=False)

    @contextmanager
    def measure(
        self,
        *,
        name: str,
        input_counts: dict[str, int | float | str | None] | None = None,
        operations: dict[str, int | float | str | None] | None = None,
    ) -> Iterator[GraphBuildStageScope]:
        scope = GraphBuildStageScope()
        if input_counts is not None:
            scope.input_counts.update(input_counts)
        if operations is not None:
            scope.operations.update(operations)

        if not self.enabled:
            yield scope
            return

        started_at = perf_counter()
        if self._started_at is None:
            self._started_at = started_at

        try:
            yield scope
        finally:
            ended_at = perf_counter()
            root_started_at = self._started_at or started_at
            metric = GraphBuildStageMetric(
                name=name,
                started_at_offset_seconds=started_at - root_started_at,
                ended_at_offset_seconds=ended_at - root_started_at,
                elapsed_seconds=ended_at - started_at,
                input_counts=dict(scope.input_counts),
                output_counts=dict(scope.output_counts),
                operations=dict(scope.operations),
            )
            self.stage_metrics.append(metric)
            self._emit_stage(metric)

    def total_elapsed_seconds(self) -> float:
        if not self.stage_metrics:
            return 0.0
        return max(
            metric.ended_at_offset_seconds
            for metric in self.stage_metrics
        )

    def _emit_stage(self, metric: GraphBuildStageMetric) -> None:
        if self.progress_callback is None:
            return
        self.progress_callback(
            f"[graph] {metric.name:<44} {metric.elapsed_seconds:>8.3f} s"
        )
