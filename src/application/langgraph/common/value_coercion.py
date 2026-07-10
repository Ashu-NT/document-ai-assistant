"""Shared scalar-coercion helpers used across the LangGraph application layer.

``optional_str`` used to be reimplemented byte-for-byte as
``nodes/node_utils.py::_optional_str`` and
``evaluation/agent_eval_runner.py::_string_or_none``. ``evaluation/
agent_eval_loader.py`` separately hand-rolled a *validating* variant of the
same idea (raising on the wrong type, used while parsing externally
authored case files) plus sibling bool/float coercions. Rather than picking
one behavior and silently changing the others, ``optional_str`` takes
``strict``/``strip`` flags so every call site's exact existing behavior is
reproduced by passing the right flags.
"""

from __future__ import annotations

from typing import Any


def optional_str(value: Any, *, strict: bool = False, strip: bool = False) -> str | None:
    """Coerce ``value`` to an optional string.

    Default (``strict=False``, ``strip=False``): mirrors the permissive
    "truthy string or None" helper used when reading tool/graph result
    payloads — non-string and falsy-string values are silently treated as
    ``None``.

    ``strict=True``: raises ``ValueError`` for any non-``None`` value that
    isn't a ``str`` (used when validating externally authored config/case
    files).

    ``strip=True``: additionally strips whitespace and treats an
    all-whitespace string as ``None``.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        if strict:
            raise ValueError("Expected string value.")
        return None
    text = value.strip() if strip else value
    return text or None


def bool_value(value: Any, *, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    raise ValueError("Expected boolean value.")


def optional_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    raise ValueError("Expected boolean or null value.")


def optional_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    raise ValueError("Expected numeric or null value.")
