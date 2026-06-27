from src.application.workflows.parsing.builders.chunking.builders.structured.family_builder_utils import (
    append_label_if_missing,
    extend_markers,
    path_contains_markers,
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

_COVER_SHEET_PATH_MARKERS = ("cover sheet",)
_GENERAL_INFORMATION_PATH_MARKERS = ("general information",)
_PARTICULARS_PATH_MARKERS = ("particulars",)
_COMPLIANCE_INFORMATION_PATH_MARKERS = ("compliance", "conformity")
_APPROVAL_INFORMATION_PATH_MARKERS = ("approval", "atex", "iecex")
_ATTACHMENT_INFORMATION_PATH_MARKERS = (
    "attachment",
    "areas inspected",
    "areas facilities inspected",
)
_TEST_DATA_PATH_MARKERS = (
    "test data",
    "results",
    "messdaten",
    "certificate 3.2",
    "abnahmeprufzeugnis",
    "abnahmeprüfzeugnis",
)
_IDENTIFICATION_TABLE_MARKERS = (
    "manufacturer designation",
    "serial number",
    "imo number",
)


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
        specs: list[StructuredSectionWindowSpec] = []

        if self._should_include_cover_sheet(
            context=context,
            base_path=base_path,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_COVER_SHEET,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=_COVER_SHEET_PATH_MARKERS,
                        label="Cover sheet",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_COVER_SHEET,
                        base_markers=CERTIFICATE_COVER_SHEET_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=1,
                    radius_after=14,
                    combine_all_windows=True,
                    include_full_section_if_no_anchor=path_contains_markers(
                        base_path,
                        _COVER_SHEET_PATH_MARKERS,
                    ),
                )
            )

        if self._should_include_general_information(
            context=context,
            base_path=base_path,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_GENERAL_INFORMATION,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=_GENERAL_INFORMATION_PATH_MARKERS,
                        label="General information",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_GENERAL_INFORMATION,
                        base_markers=CERTIFICATE_GENERAL_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=1,
                    radius_after=14,
                )
            )

        if self._should_include_particulars(
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
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=2,
                    radius_after=16,
                    combine_all_windows=True,
                    include_full_section_if_no_anchor=path_contains_markers(
                        base_path, _PARTICULARS_PATH_MARKERS
                    ),
                )
            )

        if self._should_include_compliance_information(
            context=context,
            base_path=base_path,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_COMPLIANCE_INFORMATION,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=_COMPLIANCE_INFORMATION_PATH_MARKERS,
                        label="Compliance information",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_COMPLIANCE_INFORMATION,
                        base_markers=CERTIFICATE_COMPLIANCE_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                )
            )

        if self._should_include_approval_information(
            context=context,
            base_path=base_path,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_APPROVAL_INFORMATION,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=_APPROVAL_INFORMATION_PATH_MARKERS,
                        label="Approval information",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_APPROVAL_INFORMATION,
                        base_markers=CERTIFICATE_APPROVAL_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.CERTIFICATION_INFO,
                    radius_before=1,
                    radius_after=12,
                    combine_all_windows=True,
                )
            )

        if self._should_include_test_data(
            context=context,
            base_path=base_path,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_TEST_DATA,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=_TEST_DATA_PATH_MARKERS,
                        label="Test data",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_TEST_DATA,
                        base_markers=CERTIFICATE_TEST_DATA_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                )
            )

        if self._should_include_attachment_information(
            context=context,
            base_path=base_path,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.CERTIFICATE_ATTACHMENT_INFORMATION,
                    section_path=self._family_section_path(
                        base_path=base_path,
                        family_markers=_ATTACHMENT_INFORMATION_PATH_MARKERS,
                        label="Attachment to certificate",
                    ),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.CERTIFICATE_ATTACHMENT_INFORMATION,
                        base_markers=CERTIFICATE_ATTACHMENT_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=16,
                    combine_all_windows=True,
                    include_full_section_if_no_anchor=path_contains_markers(
                        base_path,
                        _ATTACHMENT_INFORMATION_PATH_MARKERS,
                    ),
                )
            )

        return StructuredFamilySpecSelection(specs=specs)

    @staticmethod
    def _should_include_cover_sheet(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> bool:
        if path_contains_markers(base_path, _COVER_SHEET_PATH_MARKERS):
            return True
        return (
            CertificateStructuredFamilyBuilder._count_present_markers(
                context,
                CERTIFICATE_COVER_SHEET_MARKERS,
            )
            >= 2
        )

    @staticmethod
    def _should_include_general_information(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> bool:
        if path_contains_markers(base_path, _GENERAL_INFORMATION_PATH_MARKERS):
            return True
        if CertificateStructuredFamilyBuilder._looks_like_test_results(context):
            return False
        if CertificateStructuredFamilyBuilder._looks_like_identification_table(
            context
        ):
            return False
        return context.content_contains_any(CERTIFICATE_GENERAL_INFORMATION_MARKERS)

    @staticmethod
    def _should_include_particulars(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> bool:
        if CertificateStructuredFamilyBuilder._looks_like_test_results(context):
            return False
        if path_contains_markers(base_path, _PARTICULARS_PATH_MARKERS):
            return True
        if CertificateStructuredFamilyBuilder._looks_like_identification_table(
            context
        ):
            return True
        return context.content_contains_any(CERTIFICATE_PARTICULARS_MARKERS)

    @staticmethod
    def _should_include_compliance_information(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> bool:
        if CertificateStructuredFamilyBuilder._looks_like_test_results(context):
            return False
        if path_contains_markers(base_path, _COMPLIANCE_INFORMATION_PATH_MARKERS):
            return True
        return context.content_contains_any(CERTIFICATE_COMPLIANCE_INFORMATION_MARKERS)

    @staticmethod
    def _should_include_approval_information(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> bool:
        if CertificateStructuredFamilyBuilder._looks_like_test_results(context):
            return False
        if path_contains_markers(base_path, _APPROVAL_INFORMATION_PATH_MARKERS):
            return True
        return context.content_contains_any(CERTIFICATE_APPROVAL_INFORMATION_MARKERS)

    @staticmethod
    def _should_include_test_data(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> bool:
        if path_contains_markers(base_path, _TEST_DATA_PATH_MARKERS):
            return True
        return context.content_contains_any(CERTIFICATE_TEST_DATA_MARKERS)

    @staticmethod
    def _should_include_attachment_information(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> bool:
        if path_contains_markers(base_path, _ATTACHMENT_INFORMATION_PATH_MARKERS):
            return True
        return (
            CertificateStructuredFamilyBuilder._count_present_markers(
                context,
                CERTIFICATE_ATTACHMENT_INFORMATION_MARKERS,
            )
            >= 2
        )

    @staticmethod
    def _particulars_section_path(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> list[str]:
        if CertificateStructuredFamilyBuilder._looks_like_identification_table(
            context
        ):
            return ["Description / Manufacturer Designation / Serial Number table"]
        return CertificateStructuredFamilyBuilder._family_section_path(
            base_path=base_path,
            family_markers=_PARTICULARS_PATH_MARKERS,
            label="Particulars",
        )

    @staticmethod
    def _family_section_path(
        *,
        base_path: list[str],
        family_markers: tuple[str, ...],
        label: str,
    ) -> list[str]:
        if path_contains_markers(base_path, family_markers):
            return base_path
        return append_label_if_missing(base_path, label)

    @staticmethod
    def _looks_like_identification_table(
        context: StructuredFamilyContext,
    ) -> bool:
        return (
            CertificateStructuredFamilyBuilder._count_present_markers(
                context,
                _IDENTIFICATION_TABLE_MARKERS,
            )
            >= 2
        )

    @staticmethod
    def _looks_like_test_results(
        context: StructuredFamilyContext,
    ) -> bool:
        return (
            path_contains_markers(
                context.base_section_path(),
                _TEST_DATA_PATH_MARKERS,
            )
            or CertificateStructuredFamilyBuilder._count_present_markers(
                context,
                CERTIFICATE_TEST_DATA_MARKERS,
            )
            >= 2
        )

    @staticmethod
    def _count_present_markers(
        context: StructuredFamilyContext,
        markers: tuple[str, ...],
    ) -> int:
        combined_text = context.combined_text
        return sum(
            1
            for marker in markers
            if marker in combined_text
        )
