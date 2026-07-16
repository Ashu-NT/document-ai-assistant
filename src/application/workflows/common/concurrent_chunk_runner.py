from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar

# Concurrent-map-over-chunks skeleton -- used by
# extraction_workflow.py::_build_prompt (mapping
# `candidate_selector.select_for_chunk` over a batch's chunks).

ItemT = TypeVar("ItemT")
ResultT = TypeVar("ResultT")


def run_bounded_concurrent_map(
    items: list[ItemT],
    fn: Callable[[ItemT], ResultT],
    *,
    max_concurrency: int,
) -> list[ResultT]:
    max_workers = min(len(items), max_concurrency)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(fn, items))
