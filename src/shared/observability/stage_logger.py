from __future__ import annotations

import logging
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

_EVENT_NAME = "ingestion_stage"


@dataclass(slots=True)
class StageLogScope:
    """Mutable summary counts a caller fills in during a `time_stage(...)`
    block, merged into the completion log line - mirrors
    GraphBuildStageScope's ergonomics (write to it inside the `with`),
    without pulling in the heavier profiler machinery."""

    counts: dict[str, Any] = field(default_factory=dict)


def _format_fields(fields: dict[str, Any]) -> str:
    return "".join(
        f" {key}={value}" for key, value in fields.items() if value is not None
    )


def log_stage_result(
    logger: logging.Logger,
    *,
    stage_name: str,
    duration_ms: float,
    status: str,
    level: int = logging.INFO,
    document_id: str | None = None,
    ingestion_run_id: str | None = None,
    counts: dict[str, Any] | None = None,
) -> None:
    """Emit one structured stage-result log line. Shared by every stage
    boundary (GraphBuildProfiler, run_stage, IngestionStageLifecycleCoordinator,
    and the cross-reference pipeline/linkers) so the message shape stays
    consistent instead of every call site inventing its own format.

    `counts` is taken as one explicit dict (not **kwargs) deliberately -
    callers merge in arbitrary caller-supplied count dicts (e.g.
    GraphBuildStageScope.output_counts) whose keys aren't under this
    function's control and could otherwise collide with a fixed parameter
    name like `document_id`; the fixed fields are built first and `counts`
    is layered underneath them (via a fresh dict, not mutated in place) so
    a colliding count key can never shadow a fixed field, while still
    printing the fixed fields first for readability.

    One line per stage per document - never call this per chunk/per
    reference; large corpora must not flood the logs.
    """
    fixed_fields = {
        "stage": stage_name,
        "duration_ms": round(duration_ms, 1),
        "status": status,
        "document_id": document_id,
        "ingestion_run_id": ingestion_run_id,
    }
    fields: dict[str, Any] = {**fixed_fields, **{
        key: value for key, value in (counts or {}).items() if key not in fixed_fields
    }}
    logger.log(level, "%s%s", _EVENT_NAME, _format_fields(fields))


@contextmanager
def time_stage(
    logger: logging.Logger,
    stage_name: str,
    *,
    document_id: str | None = None,
    ingestion_run_id: str | None = None,
    success_level: int = logging.INFO,
    warn_if: Callable[[StageLogScope], str | None] | None = None,
) -> Generator[StageLogScope, None, None]:
    """Time one stage boundary with `time.perf_counter()` and log its
    result - `success_level` (INFO by default; pass logging.DEBUG for
    detailed resolver/candidate-level boundaries) on success, always ERROR
    (then re-raising, never swallowing) on exception. Callers write summary
    counts onto `scope.counts` during the block. `warn_if` may inspect the
    finished scope and return a WARNING message for a partial/unusual-but-
    recoverable outcome (e.g. page failures, CONFLICT rows) without
    changing the success completion line's own level.

    Use this for boundaries with no existing timing wrapper (the
    cross-reference linkers/pipeline/reconciliation service, and
    IngestionWorkflow's top-level run). Boundaries that already time
    themselves (GraphBuildProfiler, run_stage,
    IngestionStageLifecycleCoordinator) call `log_stage_result` directly at
    their existing completion point instead, reusing their own elapsed
    time rather than timing twice.
    """
    scope = StageLogScope()
    started_at = time.perf_counter()
    try:
        yield scope
    except Exception as exc:
        duration_ms = (time.perf_counter() - started_at) * 1000
        log_stage_result(
            logger,
            stage_name=stage_name,
            duration_ms=duration_ms,
            status="failed",
            level=logging.ERROR,
            document_id=document_id,
            ingestion_run_id=ingestion_run_id,
            counts={**scope.counts, "error": str(exc)},
        )
        raise

    duration_ms = (time.perf_counter() - started_at) * 1000
    warning_message = warn_if(scope) if warn_if is not None else None
    log_stage_result(
        logger,
        stage_name=stage_name,
        duration_ms=duration_ms,
        status="ok",
        level=success_level,
        document_id=document_id,
        ingestion_run_id=ingestion_run_id,
        counts=scope.counts,
    )
    if warning_message:
        logger.warning(
            "%s_warning stage=%s %s", _EVENT_NAME, stage_name, warning_message
        )


__all__ = ["StageLogScope", "log_stage_result", "time_stage"]
