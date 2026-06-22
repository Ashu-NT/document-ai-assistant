from src.application.workflows.parsing.builders.chunking.builders.structured.family_builder_utils import (
    extend_markers,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    CERTIFICATE_APPROVAL_INFORMATION_MARKERS,
    CERTIFICATE_COMPLIANCE_INFORMATION_MARKERS,
    CERTIFICATE_DOCUMENT_MARKERS,
    CERTIFICATE_GENERAL_INFORMATION_MARKERS,
    CERTIFICATE_PARTICULARS_MARKERS,
    CERTIFICATE_TEST_DATA_MARKERS,
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


class CertificateStructuredFamilyBuilder:
    def build(
        self,
        *,
        context: StructuredFamilyContext,
        marker_tuning: StructuredFamilyMarkerTuning | None,
    ) -> StructuredFamilySpecSelection:
        if (
            context.document_type != DocumentType.CERTIFICATE
            and not context.contains_any(CERTIFICATE_DOCUMENT_MARKERS)
        ):
            return StructuredFamilySpecSelection()

        return StructuredFamilySpecSelection(
            specs=[
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_GENERAL_INFORMATION,
                    section_path=["General information"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_GENERAL_INFORMATION,
                        base_markers=CERTIFICATE_GENERAL_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=1,
                    radius_after=14,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_PARTICULARS,
                    section_path=["Particulars"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_PARTICULARS,
                        base_markers=CERTIFICATE_PARTICULARS_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=2,
                    radius_after=16,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_COMPLIANCE_INFORMATION,
                    section_path=["Compliance information"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_COMPLIANCE_INFORMATION,
                        base_markers=CERTIFICATE_COMPLIANCE_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_APPROVAL_INFORMATION,
                    section_path=["Approval information"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_APPROVAL_INFORMATION,
                        base_markers=CERTIFICATE_APPROVAL_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                ),
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_TEST_DATA,
                    section_path=["Test data"],
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_TEST_DATA,
                        base_markers=CERTIFICATE_TEST_DATA_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                ),
            ]
        )
