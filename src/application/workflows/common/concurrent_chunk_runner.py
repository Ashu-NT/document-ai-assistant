from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar

# Concurrent-map-over-chunks skeleton -- previously reimplemented
# identically in extraction_workflow.py::_build_prompt (mapping
# `candidate_selector.select_for_chunk` over a batch's chunks) and
# post_classification_chunk_finalization_workflow.py::
# _classify_chunks_if_enabled (mapping `classify_chunk_without_saving`
# over the final chunk set, followed by a sequential, non-thread-safe DB
# write that stays at the call site since it isn't itself duplicated).

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
