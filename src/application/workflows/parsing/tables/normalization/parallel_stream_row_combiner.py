from __future__ import annotations

from dataclasses import dataclass

from src.application.workflows.parsing.tables.structure.table_header_label_canonicalizer import (
    TableHeaderLabelCanonicalizer,
)


@dataclass(frozen=True)
class _PreparedStream:
    rows: tuple[tuple[str, ...], ...]
    header_labels: tuple[str, ...]
    header_keys: tuple[tuple[str, int], ...]


class ParallelStreamRowCombiner:
    def __init__(
        self,
        *,
        header_label_canonicalizer: TableHeaderLabelCanonicalizer | None = None,
    ) -> None:
        self.header_label_canonicalizer = (
            header_label_canonicalizer or TableHeaderLabelCanonicalizer()
        )

    def combine(
        self,
        streams: list[list[list[str]]],
    ) -> list[list[str]] | None:
        prepared_streams = [self._prepare_stream(stream) for stream in streams]
        if any(stream is None for stream in prepared_streams):
            return None

        resolved_streams = [stream for stream in prepared_streams if stream is not None]
        if not resolved_streams:
            return None

        merged_keys = list(resolved_streams[0].header_keys)
        merged_labels = list(resolved_streams[0].header_labels)
        for stream in resolved_streams[1:]:
            merged = self._merge_header_plan(
                merged_keys=merged_keys,
                merged_labels=merged_labels,
                stream=stream,
            )
            if merged is None:
                return None
            merged_keys, merged_labels = merged

        mappings = [
            self._subsequence_positions(merged_keys, stream.header_keys)
            for stream in resolved_streams
        ]
        if any(mapping is None for mapping in mappings):
            return None

        combined_rows: list[list[str]] = [list(merged_labels)]
        for stream, mapping in zip(resolved_streams, mappings, strict=False):
            resolved_mapping = mapping or []
            for row in stream.rows[1:]:
                combined_rows.append(
                    self._project_row(
                        row=row,
                        mapping=resolved_mapping,
                        target_width=len(merged_keys),
                    )
                )
        return combined_rows

    def _prepare_stream(
        self,
        stream: list[list[str]],
    ) -> _PreparedStream | None:
        if len(stream) < 2 or not stream[0]:
            return None

        header_labels = tuple(str(cell).strip() for cell in stream[0])
        if any(not label for label in header_labels):
            return None

        header_keys = self._occurrence_keys(header_labels)
        if any(not key[0] for key in header_keys):
            return None

        rows = tuple(tuple(str(cell) for cell in row) for row in stream)
        return _PreparedStream(
            rows=rows,
            header_labels=header_labels,
            header_keys=header_keys,
        )

    def _merge_header_plan(
        self,
        *,
        merged_keys: list[tuple[str, int]],
        merged_labels: list[str],
        stream: _PreparedStream,
    ) -> tuple[list[tuple[str, int]], list[str]] | None:
        return self._build_supersequence_plan(
            left_keys=tuple(merged_keys),
            left_labels=tuple(merged_labels),
            right_keys=stream.header_keys,
            right_labels=stream.header_labels,
        )

    def _occurrence_keys(
        self,
        header_labels: tuple[str, ...],
    ) -> tuple[tuple[str, int], ...]:
        counts: dict[str, int] = {}
        keys: list[tuple[str, int]] = []
        for label in header_labels:
            canonical = self.header_label_canonicalizer.canonicalize(label)
            counts[canonical] = counts.get(canonical, 0) + 1
            keys.append((canonical, counts[canonical]))
        return tuple(keys)

    def _build_supersequence_plan(
        self,
        *,
        left_keys: tuple[tuple[str, int], ...],
        left_labels: tuple[str, ...],
        right_keys: tuple[tuple[str, int], ...],
        right_labels: tuple[str, ...],
    ) -> tuple[list[tuple[str, int]], list[str]] | None:
        common_keys = tuple(key for key in left_keys if key in set(right_keys))
        lcs = self._longest_common_subsequence(left_keys, right_keys)
        if not lcs:
            return None
        if len(lcs) != len(common_keys):
            return None
        if len(lcs) == 1 and not self._single_anchor_merge_allowed(
            left_keys=left_keys,
            right_keys=right_keys,
            anchor=lcs[0],
        ):
            return None

        left_labels_by_key = dict(zip(left_keys, left_labels, strict=False))
        right_labels_by_key = dict(zip(right_keys, right_labels, strict=False))

        merged_keys: list[tuple[str, int]] = []
        merged_labels: list[str] = []
        left_index = 0
        right_index = 0
        for anchor in lcs:
            left_index = self._append_until_anchor(
                keys=left_keys,
                labels=left_labels_by_key,
                start=left_index,
                anchor=anchor,
                merged_keys=merged_keys,
                merged_labels=merged_labels,
            )
            right_index = self._append_until_anchor(
                keys=right_keys,
                labels=right_labels_by_key,
                start=right_index,
                anchor=anchor,
                merged_keys=merged_keys,
                merged_labels=merged_labels,
            )
            merged_keys.append(anchor)
            merged_labels.append(
                self._pick_better_label(
                    left_labels_by_key[anchor],
                    right_labels_by_key[anchor],
                )
            )
            left_index += 1
            right_index += 1

        self._append_suffix(
            keys=left_keys,
            labels=left_labels_by_key,
            start=left_index,
            merged_keys=merged_keys,
            merged_labels=merged_labels,
        )
        self._append_suffix(
            keys=right_keys,
            labels=right_labels_by_key,
            start=right_index,
            merged_keys=merged_keys,
            merged_labels=merged_labels,
        )
        return merged_keys, merged_labels

    @staticmethod
    def _longest_common_subsequence(
        left: tuple[tuple[str, int], ...],
        right: tuple[tuple[str, int], ...],
    ) -> tuple[tuple[str, int], ...]:
        widths = len(right) + 1
        table: list[list[tuple[tuple[str, int], ...]]] = [
            [tuple() for _ in range(widths)] for _ in range(len(left) + 1)
        ]
        for left_index, left_key in enumerate(left, start=1):
            for right_index, right_key in enumerate(right, start=1):
                if left_key == right_key:
                    table[left_index][right_index] = (
                        table[left_index - 1][right_index - 1] + (left_key,)
                    )
                    continue
                top = table[left_index - 1][right_index]
                side = table[left_index][right_index - 1]
                table[left_index][right_index] = top if len(top) >= len(side) else side
        return table[-1][-1]

    @staticmethod
    def _single_anchor_merge_allowed(
        *,
        left_keys: tuple[tuple[str, int], ...],
        right_keys: tuple[tuple[str, int], ...],
        anchor: tuple[str, int],
    ) -> bool:
        return bool(left_keys) and bool(right_keys) and left_keys[0] == right_keys[0] == anchor

    @staticmethod
    def _append_until_anchor(
        *,
        keys: tuple[tuple[str, int], ...],
        labels: dict[tuple[str, int], str],
        start: int,
        anchor: tuple[str, int],
        merged_keys: list[tuple[str, int]],
        merged_labels: list[str],
    ) -> int:
        index = start
        while index < len(keys) and keys[index] != anchor:
            merged_keys.append(keys[index])
            merged_labels.append(labels[keys[index]])
            index += 1
        return index

    @staticmethod
    def _append_suffix(
        *,
        keys: tuple[tuple[str, int], ...],
        labels: dict[tuple[str, int], str],
        start: int,
        merged_keys: list[tuple[str, int]],
        merged_labels: list[str],
    ) -> None:
        for index in range(start, len(keys)):
            merged_keys.append(keys[index])
            merged_labels.append(labels[keys[index]])

    @staticmethod
    def _subsequence_positions(
        full: list[tuple[str, int]] | tuple[tuple[str, int], ...],
        candidate: list[tuple[str, int]] | tuple[tuple[str, int], ...],
    ) -> list[int] | None:
        positions: list[int] = []
        start = 0
        for key in candidate:
            try:
                position = list(full).index(key, start)
            except ValueError:
                return None
            positions.append(position)
            start = position + 1
        return positions

    @staticmethod
    def _project_row(
        *,
        row: tuple[str, ...],
        mapping: list[int],
        target_width: int,
    ) -> list[str]:
        projected = [""] * target_width
        for source_index, target_index in enumerate(mapping):
            if source_index >= len(row):
                continue
            projected[target_index] = row[source_index]
        return projected

    @staticmethod
    def _pick_better_label(current: str, candidate: str) -> str:
        current_clean = current.strip()
        candidate_clean = candidate.strip()
        if not current_clean:
            return candidate_clean
        if not candidate_clean:
            return current_clean

        current_score = (
            sum(character.isalpha() for character in current_clean),
            len(current_clean),
        )
        candidate_score = (
            sum(character.isalpha() for character in candidate_clean),
            len(candidate_clean),
        )
        return candidate_clean if candidate_score > current_score else current_clean
