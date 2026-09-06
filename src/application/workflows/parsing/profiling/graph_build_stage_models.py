from dataclasses import dataclass, field

GraphBuildMetricValue = int | float | str | None


@dataclass(slots=True)
class GraphBuildStageScope:
    input_counts: dict[str, GraphBuildMetricValue] = field(default_factory=dict)
    output_counts: dict[str, GraphBuildMetricValue] = field(default_factory=dict)
    operations: dict[str, GraphBuildMetricValue] = field(default_factory=dict)


@dataclass(slots=True)
class GraphBuildStageMetric:
    name: str
    started_at_offset_seconds: float
    ended_at_offset_seconds: float
    elapsed_seconds: float
    input_counts: dict[str, GraphBuildMetricValue] = field(default_factory=dict)
    output_counts: dict[str, GraphBuildMetricValue] = field(default_factory=dict)
    operations: dict[str, GraphBuildMetricValue] = field(default_factory=dict)


@dataclass(slots=True)
class GraphBuildStageAggregate:
    name: str
    started_at: float
    ended_at: float
    elapsed_seconds: float = 0.0
    invocation_count: int = 0
    input_counts: dict[str, GraphBuildMetricValue] = field(default_factory=dict)
    output_counts: dict[str, GraphBuildMetricValue] = field(default_factory=dict)
    operations: dict[str, GraphBuildMetricValue] = field(default_factory=dict)

    def add(
        self,
        *,
        started_at: float,
        ended_at: float,
        scope: GraphBuildStageScope,
    ) -> None:
        self.started_at = min(self.started_at, started_at)
        self.ended_at = max(self.ended_at, ended_at)
        self.elapsed_seconds += ended_at - started_at
        self.invocation_count += 1
        self._merge_values(self.input_counts, scope.input_counts)
        self._merge_values(self.output_counts, scope.output_counts)
        self._merge_values(self.operations, scope.operations)

    @staticmethod
    def _merge_values(
        target: dict[str, GraphBuildMetricValue],
        values: dict[str, GraphBuildMetricValue],
    ) -> None:
        for key, value in values.items():
            existing = target.get(key)
            if isinstance(existing, (int, float)) and isinstance(value, (int, float)):
                target[key] = existing + value
            elif key not in target:
                target[key] = value
