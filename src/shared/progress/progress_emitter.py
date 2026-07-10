from __future__ import annotations

from typing import Callable


def emit_progress(
    progress_callback: Callable[[str], None] | None,
    message: str,
) -> None:
    if progress_callback is not None:
        progress_callback(message)


def progress_prefix(
    *,
    index: int | None,
    total: int | None,
) -> str:
    if index is None or total is None:
        return "[seed]"
    return f"[{index}/{total}]"


def scoped_progress_callback(
    progress_callback: Callable[[str], None] | None,
    prefix: str,
) -> Callable[[str], None] | None:
    if progress_callback is None:
        return None

    def scoped_callback(message: str) -> None:
        emit_progress(progress_callback, f"{prefix} {message}")

    return scoped_callback
