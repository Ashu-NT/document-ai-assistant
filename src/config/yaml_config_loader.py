from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.shared.exceptions import SchemaValidationError


def load_yaml_config(path: Path, *, description: str) -> dict[str, Any]:
    """Load a YAML config file, raising loudly on any failure.

    No silent fallback: a missing file, a YAML parse error, or a non-mapping
    top-level value is a configuration error, not a signal to fall back to
    hardcoded Python defaults.
    """
    if not path.exists():
        raise SchemaValidationError(
            f"{description} not found.",
            details={"path": str(path)},
        )

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise SchemaValidationError(
            f"{description} could not be parsed as YAML.",
            details={"path": str(path)},
        ) from exc

    if not isinstance(data, dict):
        raise SchemaValidationError(
            f"{description} must contain a YAML mapping.",
            details={"path": str(path)},
        )
    return data
