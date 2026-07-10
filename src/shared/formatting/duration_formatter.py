from __future__ import annotations


def format_elapsed_seconds(elapsed_seconds: float) -> str:
    if elapsed_seconds < 1:
        return f"{elapsed_seconds:.2f}s"
    if elapsed_seconds < 60:
        return f"{elapsed_seconds:.1f}s"

    minutes, seconds = divmod(elapsed_seconds, 60.0)
    if minutes < 60:
        return f"{int(minutes)}m {seconds:.1f}s"

    hours, minutes = divmod(minutes, 60.0)
    return f"{int(hours)}h {int(minutes)}m {seconds:.1f}s"
