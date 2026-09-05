from src.application.workflows.parsing.builders.chunking.builders.structured.family_builder_utils import (
    extend_markers,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    DRAWING_COMPLIANCE_TABLE_MARKERS,
    DRAWING_DOCUMENT_MARKERS,
    DRAWING_EQUIPMENT_LEGEND_MARKERS,
    DRAWING_LABEL_BLOCK_MARKERS,
    DRAWING_REVISION_TABLE_MARKERS,
    DRAWING_TITLE_BLOCK_MARKERS,
    DRAWING_VESSEL_PARTICULARS_MARKERS,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_evidence_family import (
    StructuredEvidenceFamily,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_context import (
    StructuredFamilyContext,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_marker_tuning import (
    StructuredFamilyMarkerTuning,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_spec_selection import (
    StructuredFamilySpecSelection,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_section_window_spec import (
    StructuredSectionWindowSpec,
)
from src.domain.common import ChunkType, DocumentType


_TITLE_BLOCK_SECTION_TERMS = (
    "title block",
)

_REVISION_TABLE_SECTION_TERMS = (
    "revision table",
    "revision history",
    "revision record",
    "change record",
)

_VESSEL_PARTICULARS_SECTION_TERMS = (
    "vessel particulars",
    "principal particulars",
    "main particulars",
)

_LABEL_BLOCK_SECTION_TERMS = (
    "navigation lights",
    "navigation light arrangement",
    "signal lights",
    "signal light arrangement",
    "lamp labels",
    "light arrangement",
)

_COMPLIANCE_TABLE_SECTION_TERMS = (
    "colreg",
    "colregs",
    "compliance",
    "visibility arc",
)

_EQUIPMENT_LEGEND_SECTION_TERMS = (
    "equipment legend",
    "equipment list",
    "item list",
    "legend",
)


class DrawingStructuredFamilyBuilder:
    def build(
        self,
        *,
        context: StructuredFamilyContext,
        marker_tuning: StructuredFamilyMarkerTuning | None,
    ) -> StructuredFamilySpecSelection:
        has_local_drawing_evidence = (
            context.section_contains_any(DRAWING_DOCUMENT_MARKERS)
            or context.content_contains_any(DRAWING_DOCUMENT_MARKERS)
        )

        if (
            not context.matches_document_type(DocumentType.DRAWING)
            and not has_local_drawing_evidence
        ):
            return StructuredFamilySpecSelection()

        return StructuredFamilySpecSelection(
            specs=[
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DRAWING_TITLE_BLOCK,
                    section_path=["Title block"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DRAWING_TITLE_BLOCK,
                        base_markers=DRAWING_TITLE_BLOCK_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    section_context_matches=context.section_contains_any_term(
                        _TITLE_BLOCK_SECTION_TERMS
                    ),
                    chunk_type=ChunkType.GENERAL,
                    radius_before=3,
                    radius_after=8,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DRAWING_REVISION_TABLE,
                    section_path=["Revision / modification table"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DRAWING_REVISION_TABLE,
                        base_markers=DRAWING_REVISION_TABLE_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    section_context_matches=context.section_contains_any_term(
                        _REVISION_TABLE_SECTION_TERMS
                    ),
                    chunk_type=ChunkType.GENERAL,
                    radius_before=4,
                    radius_after=8,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DRAWING_VESSEL_PARTICULARS,
                    section_path=["Title block / vessel particulars"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DRAWING_VESSEL_PARTICULARS,
                        base_markers=DRAWING_VESSEL_PARTICULARS_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    section_context_matches=context.section_contains_any_term(
                        _VESSEL_PARTICULARS_SECTION_TERMS
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=6,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DRAWING_LABEL_BLOCK,
                    section_path=["Lamp labels"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DRAWING_LABEL_BLOCK,
                        base_markers=DRAWING_LABEL_BLOCK_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    section_context_matches=context.section_contains_any_term(
                        _LABEL_BLOCK_SECTION_TERMS
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=2,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DRAWING_COMPLIANCE_TABLE,
                    section_path=["COLREG table"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DRAWING_COMPLIANCE_TABLE,
                        base_markers=DRAWING_COMPLIANCE_TABLE_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    section_context_matches=context.section_contains_any_term(
                        _COMPLIANCE_TABLE_SECTION_TERMS
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=2,
                    radius_after=3,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DRAWING_EQUIPMENT_LEGEND,
                    section_path=["Equipment legend"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DRAWING_EQUIPMENT_LEGEND,
                        base_markers=DRAWING_EQUIPMENT_LEGEND_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    section_context_matches=context.section_contains_any_term(
                        _EQUIPMENT_LEGEND_SECTION_TERMS
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=8,
                ),
            ],
            consume_all_elements=True,
        )
