from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config.paths import PROJECT_ROOT

_DEFAULT_CONFIG = PROJECT_ROOT / "src" / "config" / "evaluation" / "retrieval_thresholds.yaml"


@dataclass(frozen=True)
class RetrievalQualityThresholds:
    hit_rate: float | None = 0.70
    mrr: float | None = 0.55
    recall_at_5: float | None = 0.65
    context_hit_rate: float | None = 0.60
    identifier_top_1_accuracy: float | None = 0.75

    @classmethod
    def from_yaml(cls, path: Path | str | None = None) -> RetrievalQualityThresholds:
        config_path = Path(path) if path else _DEFAULT_CONFIG
        data = _load_yaml(config_path)
        if not data:
            return cls()
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


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        return {}
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}
