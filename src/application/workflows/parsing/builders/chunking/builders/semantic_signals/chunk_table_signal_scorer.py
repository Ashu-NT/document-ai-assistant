from src.application.workflows.parsing.builders.chunking.builders.semantic_signals.chunk_type_markers import (
    NORMALIZED_TABLE_CONTENT_MARKERS,
    TABLE_SIGNAL_THRESHOLDS,
    marker_hits,
)
from src.domain.common import ChunkType


class ChunkTableSignalScorer:
    @staticmethod
    def score(content_text: str) -> dict[ChunkType, int]:
        scores: dict[ChunkType, int] = {}
        for chunk_type, markers in NORMALIZED_TABLE_CONTENT_MARKERS.items():
            hits = marker_hits(content_text, markers)
            threshold = TABLE_SIGNAL_THRESHOLDS.get(chunk_type, 2)
            if hits < threshold:
                continue
            scores[chunk_type] = min(hits + 1, 5)
        return scores

    @staticmethod
    def apply_direct_table_evidence_bias(
        scores: dict[ChunkType, int],
        table_scores: dict[ChunkType, int],
    ) -> None:
        direct_table_type = None
        if table_scores.get(ChunkType.MAINTENANCE_INTERVAL, 0) >= 3:
            direct_table_type = ChunkType.MAINTENANCE_INTERVAL
        elif table_scores.get(ChunkType.TECHNICAL_SPECIFICATION, 0) >= 4:
            direct_table_type = ChunkType.TECHNICAL_SPECIFICATION
        elif table_scores.get(ChunkType.TROUBLESHOOTING, 0) >= 4:
            direct_table_type = ChunkType.TROUBLESHOOTING

        if direct_table_type is None:
            return

        scores[direct_table_type] = scores.get(direct_table_type, 0) + 5
        if scores.get(ChunkType.SAFETY_WARNING, 0) > 0:
            scores[ChunkType.SAFETY_WARNING] = min(
                scores[ChunkType.SAFETY_WARNING],
                1,
            )
        if scores.get(ChunkType.INSTALLATION_INSTRUCTION, 0) > 0:
            scores[ChunkType.INSTALLATION_INSTRUCTION] = min(
                scores[ChunkType.INSTALLATION_INSTRUCTION],
                2,
            )
        if (
            direct_table_type in {
                ChunkType.MAINTENANCE_INTERVAL,
                ChunkType.TROUBLESHOOTING,
            }
            and scores.get(ChunkType.TECHNICAL_SPECIFICATION, 0) > 0
        ):
            scores[ChunkType.TECHNICAL_SPECIFICATION] = min(
                scores[ChunkType.TECHNICAL_SPECIFICATION],
                2,
            )
