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


class DrawingStructuredFamilyBuilder:
    def build(
        self,
        *,
        context: StructuredFamilyContext,
        marker_tuning: StructuredFamilyMarkerTuning | None,
    ) -> StructuredFamilySpecSelection:
        # Exit early only when the type is definitively non-DRAWING AND the section
        # content also lacks drawing-specific markers.  A document classified as
        # "manual" may still contain a drawing appendix whose sections carry marker
        # text ("navigation lights", "drawing number", etc.) that signals drawing
        # content — those sections should still benefit from drawing specs.
        if not context.matches_document_type(DocumentType.DRAWING) and not context.contains_any(
            DRAWING_DOCUMENT_MARKERS
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
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=0,
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
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=8,
                ),
            ],
            consume_all_elements=True,
        )
