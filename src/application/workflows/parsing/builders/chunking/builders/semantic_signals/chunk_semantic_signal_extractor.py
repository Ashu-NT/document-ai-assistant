from functools import lru_cache

from src.application.workflows.parsing.builders.chunking.builders.semantic_signals.chunk_table_signal_scorer import (
    ChunkTableSignalScorer,
)
from src.application.workflows.parsing.builders.chunking.builders.semantic_signals.chunk_type_markers import (
    CONTENT_SCORE_CAPS,
    INTERVAL_PATTERN,
    NORMALIZED_CONTENT_MARKERS,
    NORMALIZED_TITLE_MARKERS,
    SPEC_VALUE_PATTERN,
    marker_hits,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.text.section_path_sanitizer import (
    sanitize_section_path,
)
from src.application.workflows.parsing.builders.chunking.text.text_normalization import (
    normalize_comparable_text,
)
from src.domain.common import ChunkType


class ChunkSemanticSignalExtractor:
    def extract_from_fragment(
        self,
        fragment: ChunkFragment,
    ) -> dict[ChunkType, int]:
        return self.extract(
            section_title=fragment.section_title,
            section_path=fragment.section_path,
            text=fragment.text,
            table_ids=fragment.table_ids,
        )

    def extract_from_fragments(
        self,
        fragments: list[ChunkFragment],
        *,
        content: str | None = None,
    ) -> dict[ChunkType, int]:
        if not fragments:
            return {}

        aggregated: dict[ChunkType, int] = {}
        for fragment in fragments:
            for chunk_type, score in self.extract_from_fragment(fragment).items():
                aggregated[chunk_type] = aggregated.get(chunk_type, 0) + score

        if content is not None:
            for chunk_type, score in self.extract(
                section_title=fragments[0].section_title,
                section_path=fragments[0].section_path,
                text=content,
                table_ids=[
                    table_id
                    for fragment in fragments
                    for table_id in fragment.table_ids
                ],
            ).items():
                aggregated[chunk_type] = aggregated.get(chunk_type, 0) + score

        return {
            chunk_type: score
            for chunk_type, score in aggregated.items()
            if score > 0
        }

    def extract(
        self,
        *,
        section_title: str | None,
        section_path: list[str],
        text: str | None,
        table_ids: list[str] | None = None,
    ) -> dict[ChunkType, int]:
        title_text = normalize_comparable_text(section_title)
        local_path_text, ancestor_path_text = self._path_texts(tuple(section_path))
        content_text = normalize_comparable_text(text)
        scores: dict[ChunkType, int] = {}

        for chunk_type, markers in NORMALIZED_TITLE_MARKERS.items():
            title_hits = marker_hits(title_text, markers)
            if title_hits:
                scores[chunk_type] = scores.get(chunk_type, 0) + (title_hits * 4)
            local_path_hits = marker_hits(local_path_text, markers)
            ancestor_path_hits = marker_hits(ancestor_path_text, markers)
            if local_path_hits:
                scores[chunk_type] = scores.get(chunk_type, 0) + (local_path_hits * 3)
            if ancestor_path_hits:
                scores[chunk_type] = scores.get(chunk_type, 0) + self._ancestor_path_bonus(
                    chunk_type=chunk_type,
                    title_hits=title_hits,
                    local_path_hits=local_path_hits,
                    ancestor_path_hits=ancestor_path_hits,
                )

        for chunk_type, markers in NORMALIZED_CONTENT_MARKERS.items():
            content_hits = marker_hits(content_text, markers)
            if content_hits:
                cap = CONTENT_SCORE_CAPS.get(chunk_type, 2)
                scores[chunk_type] = scores.get(chunk_type, 0) + min(content_hits, 2)
                if cap != 2:
                    scores[chunk_type] = scores.get(chunk_type, 0) + (
                        min(content_hits, cap) - min(content_hits, 2)
                    )

        if INTERVAL_PATTERN.search(content_text):
            scores[ChunkType.MAINTENANCE_INTERVAL] = (
                scores.get(ChunkType.MAINTENANCE_INTERVAL, 0) + 4
            )

        if SPEC_VALUE_PATTERN.search(content_text):
            scores[ChunkType.TECHNICAL_SPECIFICATION] = (
                scores.get(ChunkType.TECHNICAL_SPECIFICATION, 0) + 2
            )

        if table_ids:
            scores[ChunkType.TECHNICAL_SPECIFICATION] = (
                scores.get(ChunkType.TECHNICAL_SPECIFICATION, 0) + 1
            )
            table_scores = ChunkTableSignalScorer.score(content_text)
            for chunk_type, bonus in table_scores.items():
                scores[chunk_type] = scores.get(chunk_type, 0) + bonus
            ChunkTableSignalScorer.apply_direct_table_evidence_bias(scores, table_scores)

        return {
            chunk_type: score
            for chunk_type, score in scores.items()
            if score > 0
        }

    @staticmethod
    def _ancestor_path_bonus(
        *,
        chunk_type: ChunkType,
        title_hits: int,
        local_path_hits: int,
        ancestor_path_hits: int,
    ) -> int:
        if chunk_type == ChunkType.SAFETY_WARNING and title_hits == 0 and local_path_hits == 0:
            return 1
        return ancestor_path_hits

    @staticmethod
    @lru_cache(maxsize=4096)
    def _path_texts(section_path: tuple[str, ...]) -> tuple[str, str]:
        sanitized_path = sanitize_section_path(list(section_path))
        normalized_parts = [
            normalize_comparable_text(segment)
            for segment in sanitized_path
            if segment
        ]
        if not normalized_parts:
            return "", ""
        if len(normalized_parts) <= 2:
            return " > ".join(normalized_parts), ""
        return " > ".join(normalized_parts[-2:]), " > ".join(normalized_parts[:-2])
