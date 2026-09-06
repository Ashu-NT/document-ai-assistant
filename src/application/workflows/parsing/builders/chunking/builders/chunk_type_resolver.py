from src.application.workflows.parsing.builders.chunking.builders.semantic_signals.chunk_semantic_signal_extractor import (
    ChunkSemanticSignalExtractor,
)
from src.application.workflows.parsing.builders.chunking.builders.semantic_signals.chunk_type_markers import (
    is_toc_remnant_text,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.domain.common import ChunkType

_SPECIAL_CHUNK_TYPES = {
    ChunkType.OVERVIEW,
    ChunkType.DRAWING_REFERENCE,
    ChunkType.SPARE_PARTS_TABLE,
    ChunkType.FORMULA,
    ChunkType.CODE_BLOCK,
    ChunkType.FORM_DATA,
}
_PROCEDURAL_TYPES = {
    ChunkType.MAINTENANCE_PROCEDURE,
    ChunkType.MAINTENANCE_INTERVAL,
    ChunkType.INSTALLATION_INSTRUCTION,
    ChunkType.OPERATION_INSTRUCTION,
}
_SPECIFICATION_TYPES = {
    ChunkType.TECHNICAL_SPECIFICATION,
    ChunkType.CERTIFICATION_INFO,
}
# Types TableFragmentBuilder.table_chunk_type() derives directly from a
# parser-assigned TableCategory (always alongside standalone=True, for both
# single-table and logical-table-family fragments) -- these are locked in
# the same way _SPECIFICATION_TYPES already is, so the classifier's keyword
# signal scores below can't second-guess and downgrade them to GENERAL.
_STANDALONE_PRESERVED_TABLE_TYPES = _SPECIFICATION_TYPES | {
    ChunkType.MAINTENANCE_INTERVAL,
    ChunkType.TROUBLESHOOTING,
    ChunkType.OPERATION_INSTRUCTION,
}


class ChunkTypeResolver:
    def __init__(
        self,
        *,
        signal_extractor: ChunkSemanticSignalExtractor | None = None,
        min_score: int = 4,
        min_gap: int = 2,
    ) -> None:
        self.signal_extractor = signal_extractor or ChunkSemanticSignalExtractor()
        self.min_score = min_score
        self.min_gap = min_gap

    def resolve(
        self,
        *,
        fragments: list[ChunkFragment],
        content: str | None = None,
    ) -> ChunkType:
        if not fragments:
            return ChunkType.GENERAL

        preserved = self._preserved_special_type(fragments)
        if preserved is not None:
            return preserved

        if self._looks_like_toc_remnant(fragments=fragments, content=content):
            return ChunkType.GENERAL

        scores = self.signal_extractor.extract_from_fragments(
            fragments,
            content=content,
        )
        if not scores:
            return ChunkType.GENERAL

        declared_type = self._qualified_declared_type(fragments, scores)
        if declared_type is not None:
            return declared_type

        ordered_scores = sorted(
            scores.items(),
            key=lambda item: (-item[1], item[0].value),
        )
        chunk_type, top_score = ordered_scores[0]
        second_type = ordered_scores[1][0] if len(ordered_scores) > 1 else None
        second_score = ordered_scores[1][1] if len(ordered_scores) > 1 else 0

        required_gap = self._required_gap(
            fragments=fragments,
            top_type=chunk_type,
            second_type=second_type,
        )
        if top_score < self.min_score or top_score - second_score < required_gap:
            return ChunkType.GENERAL

        return chunk_type

    def _qualified_declared_type(
        self,
        fragments: list[ChunkFragment],
        scores: dict[ChunkType, int],
    ) -> ChunkType | None:
        declared_types = {
            fragment.chunk_type
            for fragment in fragments
            if fragment.chunk_type not in {ChunkType.GENERAL, ChunkType.UNKNOWN}
        }
        if len(declared_types) != 1:
            return None
        declared_type = next(iter(declared_types))
        if scores.get(declared_type, 0) < max(1, self.min_score - 1):
            return None
        return declared_type

    def are_semantically_compatible(
        self,
        *,
        current_fragments: list[ChunkFragment],
        next_fragment: ChunkFragment,
    ) -> bool:
        current_families = self._strong_semantic_families(current_fragments)
        next_families = self._strong_semantic_families([next_fragment])

        if not current_families or not next_families:
            return True

        return not current_families.isdisjoint(next_families)

    def _strong_semantic_families(
        self,
        fragments: list[ChunkFragment],
    ) -> set[str]:
        scores = self.signal_extractor.extract_from_fragments(fragments)
        return {
            family
            for chunk_type, score in scores.items()
            if score >= self.min_score
            for family in [self._semantic_family(chunk_type)]
            if family is not None
        }

    def _required_gap(
        self,
        *,
        fragments: list[ChunkFragment],
        top_type: ChunkType,
        second_type: ChunkType | None,
    ) -> int:
        if (
            any(fragment.table_ids for fragment in fragments)
            and top_type in {
                ChunkType.TECHNICAL_SPECIFICATION,
                ChunkType.TROUBLESHOOTING,
            }
            and second_type == ChunkType.SAFETY_WARNING
        ):
            return 1
        return self.min_gap

    @staticmethod
    def _looks_like_toc_remnant(
        *,
        fragments: list[ChunkFragment],
        content: str | None,
    ) -> bool:
        if content is not None:
            return is_toc_remnant_text(content)
        return all(is_toc_remnant_text(fragment.text) for fragment in fragments)

    @staticmethod
    def _preserved_special_type(
        fragments: list[ChunkFragment],
    ) -> ChunkType | None:
        for fragment in fragments:
            if fragment.chunk_type in _SPECIAL_CHUNK_TYPES:
                return fragment.chunk_type

        for fragment in fragments:
            if (
                fragment.standalone
                and fragment.chunk_type in _STANDALONE_PRESERVED_TABLE_TYPES
            ):
                return fragment.chunk_type
        return None

    @staticmethod
    def _semantic_family(chunk_type: ChunkType) -> str | None:
        if chunk_type in _PROCEDURAL_TYPES:
            return "procedural"
        if chunk_type == ChunkType.SAFETY_WARNING:
            return "safety"
        if chunk_type == ChunkType.TROUBLESHOOTING:
            return "troubleshooting"
        if chunk_type in _SPECIFICATION_TYPES:
            return "specification"
        return None
