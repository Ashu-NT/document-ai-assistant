from collections import Counter, defaultdict

from src.domain.common import ChunkType
from src.domain.document import DocumentGraph


class ChunkSignalAggregator:
    """Aggregates per-chunk-type counts and per-section chunk-type signals,
    writing the section signals back onto the graph's sections."""

    @staticmethod
    def aggregate(graph: DocumentGraph) -> tuple[Counter[str], int]:
        section_signals: defaultdict[str, set[str]] = defaultdict(set)
        chunk_type_counts: Counter[str] = Counter()

        for chunk in graph.chunks.values():
            chunk_type_counts[str(chunk.chunk_type)] += 1
            if chunk.section_id and chunk.chunk_type not in {
                ChunkType.GENERAL,
                ChunkType.UNKNOWN,
            }:
                section_signals[chunk.section_id].add(str(chunk.chunk_type))

        for section_id, signals in section_signals.items():
            if section_id in graph.sections:
                graph.sections[section_id].chunk_type_signals = sorted(signals)

        return chunk_type_counts, len(section_signals)
