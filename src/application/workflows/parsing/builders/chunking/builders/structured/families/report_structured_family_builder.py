from src.application.workflows.parsing.builders.chunking.builders.structured.family_builder_utils import (
    extend_markers,
    path_contains_markers,
    sanitized_base_path,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    REPORT_ADDITIONAL_INFORMATION_MARKERS,
    REPORT_CALIBRATION_RESULTS_MARKERS,
    REPORT_CERTIFICATION_SECTION_MARKERS,
    REPORT_DEVICE_INFORMATION_MARKERS,
    REPORT_DOCUMENT_MARKERS,
    REPORT_ELECTRICAL_CONNECTION_MARKERS,
    REPORT_INSPECTION_RESULTS_MARKERS,
    REPORT_MOUNTING_MARKERS,
    REPORT_OPERATING_INSTRUCTIONS_MARKERS,
    REPORT_OPERATION_OPTIONS_MARKERS,
    REPORT_PROCEDURE_MARKERS,
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


class ReportStructuredFamilyBuilder:
    def build(
        self,
        *,
        context: StructuredFamilyContext,
        marker_tuning: StructuredFamilyMarkerTuning | None,
    ) -> StructuredFamilySpecSelection:
        if (
            context.has_known_document_type()
            and not context.matches_document_type(DocumentType.REPORT)
            and not context.contains_any(REPORT_DOCUMENT_MARKERS)
        ):
            return StructuredFamilySpecSelection()
        if (
            not context.has_known_document_type()
            and not context.contains_any(REPORT_DOCUMENT_MARKERS)
        ):
            return StructuredFamilySpecSelection()

        base_path = sanitized_base_path(
            section_path=context.base_section_path(),
            section_title=context.section.title,
            document_title=context.document_title,
        )
        # Use a dynamic section_path for the certification spec so that ATEX/approval
        # content deep in a PDF hierarchy (e.g. "Safety Instructions > Extended order
        # code > Basic specifications") gets the exact PDF-derived path rather than a
        # normalised fallback like "Manufacturer's certificates".
        certification_section_path = (
            base_path
            if path_contains_markers(base_path, ("atex", "iecex", "approval", "ex ic"))
            else ["Safety Instructions", "Manufacturer's certificates"]
        )
        return StructuredFamilySpecSelection(
            specs=[
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.REPORT_DEVICE_INFORMATION,
                    section_path=["Final Inspection Report", "Device information"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.REPORT_DEVICE_INFORMATION,
                        base_markers=REPORT_DEVICE_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=3,
                    radius_after=14,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.REPORT_ADDITIONAL_INFORMATION,
                    section_path=["Final Inspection Report", "Additional information"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.REPORT_ADDITIONAL_INFORMATION,
                        base_markers=REPORT_ADDITIONAL_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=2,
                    radius_after=12,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.REPORT_INSPECTION_RESULTS,
                    section_path=["Final Inspection Report", "Inspection results"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.REPORT_INSPECTION_RESULTS,
                        base_markers=REPORT_INSPECTION_RESULTS_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.REPORT_CALIBRATION_RESULTS,
                    section_path=["Final Inspection Report", "Calibration results"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.REPORT_CALIBRATION_RESULTS,
                        base_markers=REPORT_CALIBRATION_RESULTS_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.REPORT_ELECTRICAL_CONNECTION,
                    section_path=[
                        "Brief Operating Instructions",
                        "6 Electrical connection",
                        "6.2 Connecting the device",
                    ],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.REPORT_ELECTRICAL_CONNECTION,
                        base_markers=REPORT_ELECTRICAL_CONNECTION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.OPERATION_INSTRUCTION,
                    radius_before=2,
                    radius_after=14,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.REPORT_OPERATING_INSTRUCTIONS,
                    section_path=["Brief Operating Instructions"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.REPORT_OPERATING_INSTRUCTIONS,
                        base_markers=REPORT_OPERATING_INSTRUCTIONS_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.OPERATION_INSTRUCTION,
                    radius_before=1,
                    radius_after=10,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.REPORT_CERTIFICATION_SECTION,
                    section_path=certification_section_path,
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.REPORT_CERTIFICATION_SECTION,
                        base_markers=REPORT_CERTIFICATION_SECTION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.REPORT_PROCEDURE,
                    section_path=[
                        "Final Inspection Report",
                        "Test Procedure number / Test description",
                    ],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.REPORT_PROCEDURE,
                        base_markers=REPORT_PROCEDURE_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=2,
                    radius_after=12,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.REPORT_MOUNTING,
                    section_path=["Brief Operating Instructions", "5 Mounting"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.REPORT_MOUNTING,
                        base_markers=REPORT_MOUNTING_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.INSTALLATION_INSTRUCTION,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.REPORT_OPERATION_OPTIONS,
                    section_path=["Brief Operating Instructions", "7 Operation options"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.REPORT_OPERATION_OPTIONS,
                        base_markers=REPORT_OPERATION_OPTIONS_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.OPERATION_INSTRUCTION,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                ),
            ]
        )
