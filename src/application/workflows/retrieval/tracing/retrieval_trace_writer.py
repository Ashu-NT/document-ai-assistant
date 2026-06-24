from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from src.application.workflows.retrieval.tracing.retrieval_trace import RetrievalTrace

_DEFAULT_OUTPUT_DIR = Path("outputs/debug_retrieval")


def _to_dict(obj: object) -> object:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: _to_dict(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, list):
        return [_to_dict(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    return obj


class RetrievalTraceWriter:
    def __init__(self, output_dir: Path | str | None = None) -> None:
        self.output_dir = Path(output_dir) if output_dir else _DEFAULT_OUTPUT_DIR

    def write(self, trace: RetrievalTrace) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        safe_ts = trace.timestamp_iso.replace(":", "-").replace(".", "-")
        filename = f"trace_{trace.query_id}_{safe_ts}.json"
        path = self.output_dir / filename
        payload = _to_dict(trace)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
