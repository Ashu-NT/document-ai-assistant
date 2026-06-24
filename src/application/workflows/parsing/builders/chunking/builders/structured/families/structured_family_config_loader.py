from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config.paths import PROJECT_ROOT

_CONFIG_DIR = PROJECT_ROOT / "src" / "config" / "document_families"

_KNOWN_FILES = [
    "drawing.yaml",
    "certificate.yaml",
    "datasheet.yaml",
    "report.yaml",
    "manual.yaml",
    "sensor_list.yaml",
    "approval_information.yaml",
]


@dataclass(frozen=True)
class FamilyConfig:
    family: str
    builder_class: str
    enabled: bool
    document_type: str | None
    description: str


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        return {}
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def load_family_configs(
    config_dir: Path | None = None,
) -> list[FamilyConfig]:
    base = config_dir or _CONFIG_DIR
    configs: list[FamilyConfig] = []
    for filename in _KNOWN_FILES:
        data = _load_yaml(base / filename)
        if not data:
            continue
        try:
            cfg = FamilyConfig(
                family=str(data["family"]),
                builder_class=str(data["builder_class"]),
                enabled=bool(data.get("enabled", True)),
                document_type=data.get("document_type"),
                description=str(data.get("description", "")),
            )
            configs.append(cfg)
        except (KeyError, TypeError):
            continue
    return configs
