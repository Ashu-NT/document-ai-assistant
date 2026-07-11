from __future__ import annotations

from typing import Any


def format_page_range_label(source: Any) -> str:
    if not isinstance(source, dict):
        return ""
    page_start = source.get("page_start")
    page_end = source.get("page_end")
    if page_start is None:
        return ""
    if page_end is None or page_start == page_end:
        return f"p.{page_start}"
    return f"pp.{page_start}-{page_end}"
