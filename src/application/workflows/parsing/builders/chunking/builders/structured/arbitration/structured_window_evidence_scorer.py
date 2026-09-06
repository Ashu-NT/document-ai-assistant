import re

from src.application.workflows.parsing.builders.chunking.builders.semantic_signals.chunk_semantic_signal_extractor import (
    ChunkSemanticSignalExtractor,
)
from src.application.workflows.parsing.builders.chunking.builders.semantic_signals.chunk_type_markers import (
    INTERVAL_PATTERN,
    SPEC_VALUE_PATTERN,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_element_text_resolver import (
    StructuredElementTextResolver,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_section_window_spec import (
    StructuredSectionWindowSpec,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    resolve_parser_extra,
)
from src.application.workflows.shared.table_category_chunk_type import (
    chunk_type_for_table_category,
)
from src.domain.common import ChunkType, ElementType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


_PART_VALUE_PATTERN = re.compile(
    r"\b(?:part|item|position)\s*(?:no|number|#)\s*[:=]?\s*[a-z0-9][a-z0-9./_-]{2,}\b",
    re.IGNORECASE,
)
_TROUBLESHOOTING_PAIR_PATTERN = re.compile(
    r"\b(?:possible|probable)?\s*(?:cause|problem|symptom)\b.*"
    r"\b(?:remedy|corrective\s+action|solution|measure|action)\b",
    re.IGNORECASE | re.DOTALL,
)
_SAFETY_CALLOUT_PATTERN = re.compile(
    r"^\s*(?:warning|caution|danger|notice|hazard)\b",
    re.IGNORECASE,
)
_PROCEDURAL_TYPES = {
    ChunkType.MAINTENANCE_PROCEDURE,
    ChunkType.INSTALLATION_INSTRUCTION,
    ChunkType.OPERATION_INSTRUCTION,
}


class StructuredWindowEvidenceScorer:
    def __init__(
        self,
        *,
        signal_extractor: ChunkSemanticSignalExtractor | None = None,
    ) -> None:
        self.signal_extractor = signal_extractor or ChunkSemanticSignalExtractor()

    def score(
        self,
        *,
        section: DocumentSection,
        spec: StructuredSectionWindowSpec,
        elements: tuple[CanonicalElement, ...],
        marker_score: int,
    ) -> tuple[int, bool]:
        content = "\n".join(
            text
            for element in elements
            if (text := StructuredElementTextResolver.resolve(element))
        )
        table_ids = [
            element.table_id for element in elements if element.table_id is not None
        ]
        semantic_score = self.signal_extractor.extract(
            section_title=section.title,
            section_path=list(section.section_path),
            text=content,
            table_ids=table_ids,
        ).get(spec.chunk_type, 0)
        direct_score = self._direct_evidence_score(
            spec=spec,
            elements=elements,
            content=content,
        )
        context_matches = (
            spec.section_context_matches
            or spec.include_full_section_if_no_anchor
        )
        direct_evidence = direct_score > 0 or context_matches
        context_score = 4 if context_matches else 0
        return marker_score + min(semantic_score, 8) + direct_score + context_score, direct_evidence

    def has_direct_evidence(
        self,
        *,
        spec: StructuredSectionWindowSpec,
        elements: tuple[CanonicalElement, ...],
    ) -> bool:
        content = "\n".join(
            text
            for element in elements
            if (text := StructuredElementTextResolver.resolve(element))
        )
        return self._direct_evidence_score(
            spec=spec,
            elements=elements,
            content=content,
        ) > 0

    def _direct_evidence_score(
        self,
        *,
        spec: StructuredSectionWindowSpec,
        elements: tuple[CanonicalElement, ...],
        content: str,
    ) -> int:
        category_score = self._table_category_score(spec, elements)
        if category_score:
            return category_score
        if spec.chunk_type == ChunkType.MAINTENANCE_INTERVAL and INTERVAL_PATTERN.search(content):
            return 7
        if spec.chunk_type == ChunkType.TECHNICAL_SPECIFICATION and SPEC_VALUE_PATTERN.search(content):
            return 6
        if spec.chunk_type == ChunkType.SPARE_PARTS_TABLE and _PART_VALUE_PATTERN.search(content):
            return 7
        if spec.chunk_type == ChunkType.TROUBLESHOOTING and _TROUBLESHOOTING_PAIR_PATTERN.search(content):
            return 7
        if spec.chunk_type == ChunkType.SAFETY_WARNING and _SAFETY_CALLOUT_PATTERN.search(content):
            return 6
        if spec.chunk_type in _PROCEDURAL_TYPES:
            list_count = sum(
                element.element_type == ElementType.LIST_ITEM for element in elements
            )
            if list_count >= 2:
                return 5
        if (
            spec.chunk_type in {ChunkType.TECHNICAL_SPECIFICATION, ChunkType.CERTIFICATION_INFO}
            and any(element.element_type == ElementType.KEY_VALUE for element in elements)
        ):
            return 5
        return 0

    @staticmethod
    def _table_category_score(
        spec: StructuredSectionWindowSpec,
        elements: tuple[CanonicalElement, ...],
    ) -> int:
        for element in elements:
            category = resolve_parser_extra(element).get("table_category")
            if chunk_type_for_table_category(category) == spec.chunk_type:
                return 10
        return 0
