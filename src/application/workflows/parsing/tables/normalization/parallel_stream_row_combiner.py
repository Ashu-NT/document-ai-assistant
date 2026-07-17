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
        if self._is_subsequence(stream.header_keys, merged_keys):
            return self._adopt_other_plan(
                base_keys=list(merged_keys),
                base_labels=list(merged_labels),
                other_keys=list(stream.header_keys),
                other_labels=list(stream.header_labels),
            )
        if self._is_subsequence(merged_keys, stream.header_keys):
            return self._enrich_existing_labels(
                base_keys=list(merged_keys),
                base_labels=list(merged_labels),
                other_keys=list(stream.header_keys),
                other_labels=list(stream.header_labels),
            )
        return None

    def _adopt_other_plan(
        self,
        *,
        base_keys: list[tuple[str, int]],
        base_labels: list[str],
        other_keys: list[tuple[str, int]],
        other_labels: list[str],
    ) -> tuple[list[tuple[str, int]], list[str]]:
        merged_labels_by_key = {
            key: label
            for key, label in zip(other_keys, other_labels, strict=False)
        }
        base_mapping = self._subsequence_positions(other_keys, tuple(base_keys)) or []
        for base_index, target_index in enumerate(base_mapping):
            merged_labels_by_key[other_keys[target_index]] = self._pick_better_label(
                merged_labels_by_key[other_keys[target_index]],
                base_labels[base_index],
            )
        merged_labels = [merged_labels_by_key[key] for key in other_keys]
        return other_keys, merged_labels

    def _enrich_existing_labels(
        self,
        *,
        base_keys: list[tuple[str, int]],
        base_labels: list[str],
        other_keys: list[tuple[str, int]],
        other_labels: list[str],
    ) -> tuple[list[tuple[str, int]], list[str]]:
        mapping = self._subsequence_positions(tuple(base_keys), tuple(other_keys)) or []
        enriched = list(base_labels)
        for other_index, target_index in enumerate(mapping):
            enriched[target_index] = self._pick_better_label(
                enriched[target_index],
                other_labels[other_index],
            )
        return base_keys, enriched

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

    @staticmethod
    def _is_subsequence(
        longer: list[tuple[str, int]] | tuple[tuple[str, int], ...],
        shorter: list[tuple[str, int]] | tuple[tuple[str, int], ...],
    ) -> bool:
        return ParallelStreamRowCombiner._subsequence_positions(longer, shorter) is not None

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
