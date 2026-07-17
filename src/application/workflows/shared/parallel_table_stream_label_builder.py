from __future__ import annotations

from src.domain.assets import TableParallelStream


class ParallelTableStreamLabelBuilder:
    _POSITION_LABELS = {
        2: {1: "Left", 2: "Right"},
        3: {1: "Left", 2: "Center", 3: "Right"},
    }

    def build_title(
        self,
        *,
        stream_index: int,
        stream_count: int,
        descriptor: TableParallelStream | None = None,
    ) -> str:
        _ = descriptor
        position = self._position_label(
            stream_index=stream_index,
            stream_count=stream_count,
        )
        if position is None:
            return f"Parallel Table Stream {stream_index}"
        return f"Parallel Table Stream {stream_index} ({position})"

    def build_short_label(
        self,
        *,
        stream_index: int,
        stream_count: int,
        descriptor: TableParallelStream | None = None,
    ) -> str:
        _ = descriptor
        return self._position_label(
            stream_index=stream_index,
            stream_count=stream_count,
        ) or f"Stream {stream_index}"

    def _position_label(
        self,
        *,
        stream_index: int,
        stream_count: int,
    ) -> str | None:
        return self._POSITION_LABELS.get(stream_count, {}).get(stream_index)
