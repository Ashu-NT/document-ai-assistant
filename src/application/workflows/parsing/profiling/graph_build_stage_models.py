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
