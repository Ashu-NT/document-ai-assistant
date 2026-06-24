from __future__ import annotations

from pathlib import Path
from typing import Any

from src.application.workflows.parsing.markers.marker_set import MarkerSet
from src.config.paths import PROJECT_ROOT

_CONFIG_DIR = PROJECT_ROOT / "src" / "config" / "markers"

_KNOWN_FILES: dict[str, str] = {
    "manual": "manual.yaml",
    "certificate": "certificate.yaml",
    "datasheet": "datasheet.yaml",
    "drawing": "drawing.yaml",
    "report": "report.yaml",
    "sensor": "sensor.yaml",
    "common": "common.yaml",
}


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


def load_marker_set(
    family: str,
    *,
    config_dir: Path | None = None,
) -> MarkerSet | None:
    base = config_dir or _CONFIG_DIR
    filename = _KNOWN_FILES.get(family)
    if filename is None:
        return None
    data = _load_yaml(base / filename)
    if not data:
        return None
    markers = {
        k: tuple(str(v) for v in vals) if isinstance(vals, list) else ()
        for k, vals in data.items()
        if isinstance(vals, list)
    }
    return MarkerSet(name=family, markers=markers)
