from __future__ import annotations

import logging
from contextlib import contextmanager
from time import perf_counter
from typing import Generator

from src.application.workflows.parsing.profiling.graph_build_stage_models import (
    GraphBuildStageMetric,
    GraphBuildStageScope,
)
from src.config.logging import get_logger
from src.shared.observability.stage_logger import log_stage_result

_logger = get_logger(__name__)


class GraphBuildProfiler:
    def __init__(
        self,
        *,
        enabled: bool = True,
        progress_callback=None,
        document_id: str | None = None,
    ) -> None:
        self.enabled = enabled
        self.progress_callback = progress_callback
        self.document_id = document_id
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
    ) -> Generator[GraphBuildStageScope, None, None]:
        scope = GraphBuildStageScope()
        if input_counts is not None:
            scope.input_counts.update(input_counts)
        if operations is not None:
            scope.operations.update(operations)

        started_at = perf_counter()
        if self.enabled and self._started_at is None:
            self._started_at = started_at

        try:
            yield scope
        except Exception as exc:
            elapsed_seconds = perf_counter() - started_at
            log_stage_result(
                _logger,
                stage_name=name,
                duration_ms=elapsed_seconds * 1000,
                status="failed",
                level=logging.ERROR,
                document_id=self.document_id,
                counts={**scope.input_counts, "error": str(exc)},
            )
            raise

        ended_at = perf_counter()
        elapsed_seconds = ended_at - started_at
        # One INFO line per named stage regardless of self.enabled - cheap
        # (a handful of stages per document, never per chunk/reference) and
        # this is what makes a real corpus run observable at all; the
        # detailed GraphBuildStageMetric history below stays opt-in since
        # that's for the heavier profile_graph_build.py report, a separate
        # concern from basic stage logging.
        log_stage_result(
            _logger,
            stage_name=name,
            duration_ms=elapsed_seconds * 1000,
            status="ok",
            document_id=self.document_id,
            counts={**scope.input_counts, **scope.output_counts},
        )

        if self.enabled:
            root_started_at = self._started_at or started_at
            metric = GraphBuildStageMetric(
                name=name,
                started_at_offset_seconds=started_at - root_started_at,
                ended_at_offset_seconds=ended_at - root_started_at,
                elapsed_seconds=elapsed_seconds,
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
