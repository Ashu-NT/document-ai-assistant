from src.application.workflows.parsing.builders.chunking.builders.structured.family_builder_utils import (
    append_label_if_missing,
    extend_markers,
    path_contains_markers,
    sanitized_base_path,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    MANUAL_COMMISSIONING_MARKERS,
    MANUAL_DOCUMENT_MARKERS,
    MANUAL_INSTALLATION_MARKERS,
    MANUAL_LUBRICATION_MARKERS,
    MANUAL_MAINTENANCE_INTERVAL_MARKERS,
    MANUAL_MAINTENANCE_PROCEDURE_MARKERS,
    MANUAL_OPERATION_MARKERS,
    MANUAL_SAFETY_MARKERS,
    MANUAL_SHUTDOWN_MARKERS,
    MANUAL_SPARE_PARTS_MARKERS,
    MANUAL_TROUBLESHOOTING_MARKERS,
    SENSOR_DOCUMENT_MARKERS,
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

_TROUBLESHOOTING_PATH_MARKERS = ("troubleshooting", "trouble shooting")
_SPARE_PARTS_PATH_MARKERS = ("spare parts", "parts list")
_COMMISSIONING_PATH_MARKERS = ("commissioning",)
_SHUTDOWN_PATH_MARKERS = ("shutdown", "shut down")
_SAFETY_PATH_MARKERS = ("safety", "warning")


class ManualStructuredFamilyBuilder:
    def build(
        self,
        *,
        context: StructuredFamilyContext,
        marker_tuning: StructuredFamilyMarkerTuning | None,
    ) -> StructuredFamilySpecSelection:
        if (
            context.has_known_document_type()
            and not context.matches_document_type(DocumentType.MANUAL)
        ):
            return StructuredFamilySpecSelection()
        if (
            not context.has_known_document_type()
            and not context.contains_any(MANUAL_DOCUMENT_MARKERS)
        ):
            return StructuredFamilySpecSelection()
        if context.contains_any(SENSOR_DOCUMENT_MARKERS):
            return StructuredFamilySpecSelection()

        base_path = sanitized_base_path(
            section_path=context.base_section_path(),
            section_title=context.section.title,
            document_title=context.document_title,
        )
        has_interval_signal = context.contains_any(MANUAL_MAINTENANCE_INTERVAL_MARKERS)
        return StructuredFamilySpecSelection(
            specs=[
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.MANUAL_OPERATION_PROCEDURE,
                    section_path=base_path,
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.MANUAL_OPERATION_PROCEDURE,
                        base_markers=MANUAL_OPERATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.OPERATION_INSTRUCTION,
                    radius_before=2,
                    radius_after=10,
                    combine_all_windows=True,
                ),
                *(
                    []
                    if has_interval_signal
                    else [
                        StructuredSectionWindowSpec(
                            family=StructuredEvidenceFamily.MANUAL_MAINTENANCE_PROCEDURE,
                            section_path=base_path,
                            anchor_markers=extend_markers(
                                family=StructuredEvidenceFamily.MANUAL_MAINTENANCE_PROCEDURE,
                                base_markers=MANUAL_MAINTENANCE_PROCEDURE_MARKERS,
                                marker_tuning=marker_tuning,
                            ),
                            chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
                            radius_before=2,
                            radius_after=12,
                        )
                    ]
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.MANUAL_MAINTENANCE_INTERVAL,
                    section_path=append_label_if_missing(base_path, "Maintenance Intervals"),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.MANUAL_MAINTENANCE_INTERVAL,
                        base_markers=MANUAL_MAINTENANCE_INTERVAL_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.MAINTENANCE_INTERVAL,
                    radius_before=1,
                    radius_after=18,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.MANUAL_TROUBLESHOOTING,
                    section_path=(
                        base_path
                        if path_contains_markers(base_path, _TROUBLESHOOTING_PATH_MARKERS)
                        else append_label_if_missing(base_path, "Troubleshooting")
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.MANUAL_TROUBLESHOOTING,
                        base_markers=MANUAL_TROUBLESHOOTING_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TROUBLESHOOTING,
                    radius_before=2,
                    radius_after=18,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.MANUAL_SPARE_PARTS,
                    section_path=(
                        base_path
                        if path_contains_markers(base_path, _SPARE_PARTS_PATH_MARKERS)
                        else append_label_if_missing(base_path, "Spare Parts")
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.MANUAL_SPARE_PARTS,
                        base_markers=MANUAL_SPARE_PARTS_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.SPARE_PARTS_TABLE,
                    radius_before=1,
                    radius_after=10,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.MANUAL_COMMISSIONING,
                    section_path=(
                        base_path
                        if path_contains_markers(base_path, _COMMISSIONING_PATH_MARKERS)
                        else append_label_if_missing(base_path, "Commissioning")
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.MANUAL_COMMISSIONING,
                        base_markers=MANUAL_COMMISSIONING_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.OPERATION_INSTRUCTION,
                    radius_before=2,
                    radius_after=12,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.MANUAL_SHUTDOWN,
                    section_path=(
                        base_path
                        if path_contains_markers(base_path, _SHUTDOWN_PATH_MARKERS)
                        else append_label_if_missing(base_path, "Shutdown")
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.MANUAL_SHUTDOWN,
                        base_markers=MANUAL_SHUTDOWN_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
                    radius_before=2,
                    radius_after=12,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.MANUAL_SAFETY_INSTRUCTIONS,
                    section_path=(
                        base_path
                        if path_contains_markers(base_path, _SAFETY_PATH_MARKERS)
                        else append_label_if_missing(base_path, "Safety Instructions")
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.MANUAL_SAFETY_INSTRUCTIONS,
                        base_markers=MANUAL_SAFETY_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.SAFETY_WARNING,
                    radius_before=1,
                    radius_after=10,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.MANUAL_LUBRICATION,
                    section_path=base_path,
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.MANUAL_LUBRICATION,
                        base_markers=MANUAL_LUBRICATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.MAINTENANCE_INTERVAL,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.MANUAL_INSTALLATION,
                    section_path=base_path,
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.MANUAL_INSTALLATION,
                        base_markers=MANUAL_INSTALLATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.INSTALLATION_INSTRUCTION,
                    radius_before=1,
                    radius_after=10,
                    combine_all_windows=True,
                ),
            ]
        )
