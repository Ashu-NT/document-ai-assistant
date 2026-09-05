from src.application.workflows.parsing.builders.chunking.builders.structured.families.certificate.certificate_inclusion_policy import (
    APPROVAL_INFORMATION_PATH_MARKERS,
    ATTACHMENT_INFORMATION_PATH_MARKERS,
    CertificateInclusionPolicy,
    COMPLIANCE_INFORMATION_PATH_MARKERS,
    COVER_SHEET_PATH_MARKERS,
    GENERAL_INFORMATION_PATH_MARKERS,
    PARTICULARS_PATH_MARKERS,
    TEST_DATA_PATH_MARKERS,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.family_builder_utils import (
    append_label_if_missing,
    extend_markers,
    path_contains_terms,
    sanitized_base_path,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    CERTIFICATE_ATTACHMENT_INFORMATION_MARKERS,
    CERTIFICATE_APPROVAL_INFORMATION_MARKERS,
    CERTIFICATE_COMPLIANCE_INFORMATION_MARKERS,
    CERTIFICATE_COVER_SHEET_MARKERS,
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
            context.has_known_document_type()
            and not context.matches_document_type(DocumentType.CERTIFICATE)
            and not context.contains_any(CERTIFICATE_DOCUMENT_MARKERS)
        ):
            return StructuredFamilySpecSelection()

        if (
            not context.has_known_document_type()
            and not context.contains_any(CERTIFICATE_DOCUMENT_MARKERS)
        ):
            return StructuredFamilySpecSelection()

        base_path = sanitized_base_path(
            section_path=context.base_section_path(),
            section_title=context.section.title,
            document_title=context.document_title,
        )

        base_has_cover_sheet_path = path_contains_terms(
            base_path,
            COVER_SHEET_PATH_MARKERS,
        )
        base_has_general_information_path = path_contains_terms(
            base_path,
            GENERAL_INFORMATION_PATH_MARKERS,
        )
        base_has_particulars_path = path_contains_terms(
            base_path,
            PARTICULARS_PATH_MARKERS,
        )
        base_has_compliance_information_path = path_contains_terms(
            base_path,
            COMPLIANCE_INFORMATION_PATH_MARKERS,
        )
        base_has_approval_information_path = path_contains_terms(
            base_path,
            APPROVAL_INFORMATION_PATH_MARKERS,
        )
        base_has_test_data_path = path_contains_terms(
            base_path,
            TEST_DATA_PATH_MARKERS,
        )
        base_has_attachment_information_path = path_contains_terms(
            base_path,
            ATTACHMENT_INFORMATION_PATH_MARKERS,
        )

        specs: list[StructuredSectionWindowSpec] = []

        if CertificateInclusionPolicy.should_include_cover_sheet(
            context=context,
            base_path=base_path,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_COVER_SHEET,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=COVER_SHEET_PATH_MARKERS,
                        label="Cover sheet",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_COVER_SHEET,
                        base_markers=CERTIFICATE_COVER_SHEET_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    section_context_matches=base_has_cover_sheet_path,
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=1,
                    radius_after=14,
                    combine_all_windows=True,
                    include_full_section_if_no_anchor=base_has_cover_sheet_path,
                )
            )

        if CertificateInclusionPolicy.should_include_general_information(
            context=context,
            base_path=base_path,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_GENERAL_INFORMATION,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=GENERAL_INFORMATION_PATH_MARKERS,
                        label="General information",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_GENERAL_INFORMATION,
                        base_markers=CERTIFICATE_GENERAL_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    section_context_matches=base_has_general_information_path,
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=1,
                    radius_after=14,
                )
            )

        if CertificateInclusionPolicy.should_include_particulars(
            context=context,
            base_path=base_path,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_PARTICULARS,
                    section_path=self._particulars_section_path(
                        context=context,
                        base_path=base_path,
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_PARTICULARS,
                        base_markers=CERTIFICATE_PARTICULARS_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    section_context_matches=base_has_particulars_path,
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=2,
                    radius_after=16,
                    combine_all_windows=True,
                    include_full_section_if_no_anchor=base_has_particulars_path,
                )
            )

        if CertificateInclusionPolicy.should_include_compliance_information(
            context=context,
            base_path=base_path,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_COMPLIANCE_INFORMATION,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=COMPLIANCE_INFORMATION_PATH_MARKERS,
                        label="Compliance information",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_COMPLIANCE_INFORMATION,
                        base_markers=CERTIFICATE_COMPLIANCE_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    section_context_matches=base_has_compliance_information_path,
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                )
            )

        if CertificateInclusionPolicy.should_include_approval_information(
            context=context,
            base_path=base_path,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_APPROVAL_INFORMATION,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=APPROVAL_INFORMATION_PATH_MARKERS,
                        label="Approval information",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_APPROVAL_INFORMATION,
                        base_markers=CERTIFICATE_APPROVAL_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    section_context_matches=base_has_approval_information_path,
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                )
            )

        if CertificateInclusionPolicy.should_include_test_data(
            context=context,
            base_path=base_path,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_TEST_DATA,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=TEST_DATA_PATH_MARKERS,
                        label="Test data",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_TEST_DATA,
                        base_markers=CERTIFICATE_TEST_DATA_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    section_context_matches=base_has_test_data_path,
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                )
            )

        if CertificateInclusionPolicy.should_include_attachment_information(
            context=context,
            base_path=base_path,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_ATTACHMENT_INFORMATION,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=ATTACHMENT_INFORMATION_PATH_MARKERS,
                        label="Attachment to certificate",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_ATTACHMENT_INFORMATION,
                        base_markers=CERTIFICATE_ATTACHMENT_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    section_context_matches=base_has_attachment_information_path,
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=16,
                    combine_all_windows=True,
                    include_full_section_if_no_anchor=(
                        base_has_attachment_information_path
                    ),
                )
            )

        return StructuredFamilySpecSelection(
            specs=specs,
        )

    @staticmethod
    def _particulars_section_path(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> list[str]:
        if CertificateInclusionPolicy.looks_like_identification_table(
            context
        ):
            return [
                "Description / Manufacturer Designation / Serial Number table"
            ]

        return CertificateStructuredFamilyBuilder._family_section_path(
            base_path=base_path,
            family_markers=PARTICULARS_PATH_MARKERS,
            label="Particulars",
        )

    @staticmethod
    def _family_section_path(
        *,
        base_path: list[str],
        family_markers: tuple[str, ...],
        label: str,
    ) -> list[str]:
        if path_contains_terms(
            base_path,
            family_markers,
        ):
            return base_path

        return append_label_if_missing(
            base_path,
            label,
        )