from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config.paths import PROJECT_ROOT
from src.config.yaml_config_loader import load_yaml_config

_DEFAULT_CONFIG = PROJECT_ROOT / "src" / "config" / "evaluation" / "retrieval_thresholds.yaml"


@dataclass(frozen=True)
class RetrievalQualityThresholds:
    hit_rate: float | None
    mrr: float | None
    recall_at_5: float | None
    context_hit_rate: float | None
    identifier_top_1_accuracy: float | None

    @classmethod
    def from_yaml(cls, path: Path | str | None = None) -> RetrievalQualityThresholds:
        config_path = Path(path) if path else _DEFAULT_CONFIG
        data = load_yaml_config(
            config_path,
            description="Retrieval quality thresholds",
        )
        return cls(
            hit_rate=_opt_float(data.get("hit_rate")),
            mrr=_opt_float(data.get("mrr")),
            recall_at_5=_opt_float(data.get("recall_at_5")),
            context_hit_rate=_opt_float(data.get("context_hit_rate")),
            identifier_top_1_accuracy=_opt_float(
                data.get("identifier_top_1_accuracy")
            ),
        )


def _opt_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)
