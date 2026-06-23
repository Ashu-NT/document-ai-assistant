from src.application.workflows.parsing.builders.chunking.builders.structured.family_builder_utils import (
    extend_markers,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    DATASHEET_CONNECTION_INFORMATION_MARKERS,
    DATASHEET_DOCUMENT_MARKERS,
    DATASHEET_MATERIAL_INFORMATION_MARKERS,
    DATASHEET_OPERATING_LIMITS_MARKERS,
    DATASHEET_ORDERING_EXAMPLE_MARKERS,
    DATASHEET_ORDERING_INFORMATION_MARKERS,
    DATASHEET_PRESSURE_TEMPERATURE_MARKERS,
    DATASHEET_SPECIFICATION_TABLE_MARKERS,
    DATASHEET_TECHNICAL_DATA_MARKERS,
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


class DatasheetStructuredFamilyBuilder:
    def build(
        self,
        *,
        context: StructuredFamilyContext,
        marker_tuning: StructuredFamilyMarkerTuning | None,
    ) -> StructuredFamilySpecSelection:
        if (
            context.has_known_document_type()
            and not context.matches_document_type(DocumentType.DATASHEET)
            and not context.contains_any(DATASHEET_DOCUMENT_MARKERS)
        ):
            return StructuredFamilySpecSelection()
        if (
            not context.has_known_document_type()
            and not context.contains_any(DATASHEET_DOCUMENT_MARKERS)
        ):
            return StructuredFamilySpecSelection()

        return StructuredFamilySpecSelection(
            specs=[
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_TECHNICAL_DATA,
                    section_path=["Technical Data / Specification"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_TECHNICAL_DATA,
                        base_markers=DATASHEET_TECHNICAL_DATA_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=14,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_SPECIFICATION_TABLE,
                    section_path=["Technical Data / Specification"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_SPECIFICATION_TABLE,
                        base_markers=DATASHEET_SPECIFICATION_TABLE_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=14,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_ORDERING_INFORMATION,
                    section_path=["Ordering information"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_ORDERING_INFORMATION,
                        base_markers=DATASHEET_ORDERING_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=10,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_ORDERING_EXAMPLE,
                    section_path=["Ordering example"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_ORDERING_EXAMPLE,
                        base_markers=DATASHEET_ORDERING_EXAMPLE_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=2,
                    radius_after=10,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_CONNECTION_INFORMATION,
                    section_path=["CONNECTION"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_CONNECTION_INFORMATION,
                        base_markers=DATASHEET_CONNECTION_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=10,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_OPERATING_LIMITS,
                    section_path=["Operating limits"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_OPERATING_LIMITS,
                        base_markers=DATASHEET_OPERATING_LIMITS_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_PRESSURE_TEMPERATURE_DATA,
                    section_path=[
                        "Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram"
                    ],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_PRESSURE_TEMPERATURE_DATA,
                        base_markers=DATASHEET_PRESSURE_TEMPERATURE_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=2,
                    radius_after=14,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.DATASHEET_MATERIAL_INFORMATION,
                    section_path=["Material information"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.DATASHEET_MATERIAL_INFORMATION,
                        base_markers=DATASHEET_MATERIAL_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=10,
                ),
            ]
        )
