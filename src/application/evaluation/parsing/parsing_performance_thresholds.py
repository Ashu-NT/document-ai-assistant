from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config.paths import PROJECT_ROOT
from src.config.yaml_config_loader import load_yaml_config

_DEFAULT_CONFIG = (
    PROJECT_ROOT / "src" / "config" / "evaluation" / "parsing_performance_thresholds.yaml"
)


@dataclass(frozen=True)
class ParsingPerformanceThresholds:
    docling_conversion_max_seconds: float | None
    canonical_normalization_max_seconds: float | None
    graph_build_max_seconds: float | None
    total_max_seconds: float | None

    @classmethod
    def from_yaml(cls, path: Path | str | None = None) -> ParsingPerformanceThresholds:
        config_path = Path(path) if path else _DEFAULT_CONFIG
        data = load_yaml_config(
            config_path,
            description="Parsing performance thresholds",
        )
        return cls(
            docling_conversion_max_seconds=_opt_float(
                data.get("docling_conversion_max_seconds")
            ),
            canonical_normalization_max_seconds=_opt_float(
                data.get("canonical_normalization_max_seconds")
            ),
            graph_build_max_seconds=_opt_float(data.get("graph_build_max_seconds")),
            total_max_seconds=_opt_float(data.get("total_max_seconds")),
        )


def _opt_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)
