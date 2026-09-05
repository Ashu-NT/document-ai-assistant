from src.application.workflows.parsing.builders.chunking.builders.structured.family_builder_utils import (
    path_contains_markers, path_contains_terms
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    CERTIFICATE_ATTACHMENT_INFORMATION_MARKERS,
    CERTIFICATE_APPROVAL_INFORMATION_MARKERS,
    CERTIFICATE_COMPLIANCE_INFORMATION_MARKERS,
    CERTIFICATE_COVER_SHEET_MARKERS,
    CERTIFICATE_GENERAL_INFORMATION_MARKERS,
    CERTIFICATE_PARTICULARS_MARKERS,
    CERTIFICATE_TEST_DATA_MARKERS,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerStrength,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    StructuredMarkerMatcher,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_family_context import (
    StructuredFamilyContext,
)

COVER_SHEET_PATH_MARKERS = ("cover sheet",)
GENERAL_INFORMATION_PATH_MARKERS = ("general information",)
PARTICULARS_PATH_MARKERS = ("particulars",)
COMPLIANCE_INFORMATION_PATH_MARKERS = ("compliance", "conformity")
APPROVAL_INFORMATION_PATH_MARKERS = ("approval", "atex", "iecex")
ATTACHMENT_INFORMATION_PATH_MARKERS = (
    "attachment",
    "areas inspected",
    "areas facilities inspected",
)
TEST_DATA_PATH_MARKERS = (
    "test data",
    "results",
    "messdaten",
    "certificate 3.2",
    "abnahmeprufzeugnis",
    "abnahmeprüfzeugnis",
)
IDENTIFICATION_TABLE_MARKERS = (
    EvidenceMarker(
        "manufacturer designation",
        MarkerStrength.STRONG,
    ),
    EvidenceMarker(
        "serial number",
        MarkerStrength.MEDIUM,
    ),
    EvidenceMarker(
        "imo number",
        MarkerStrength.MEDIUM,
    ),
)
_MARKER_MATCHER = StructuredMarkerMatcher()


class CertificateInclusionPolicy:
    @staticmethod
    def should_include_cover_sheet(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> bool:
        if path_contains_terms(base_path, COVER_SHEET_PATH_MARKERS):
            return True
        return (
            CertificateInclusionPolicy._count_present_markers(
                context,
                CERTIFICATE_COVER_SHEET_MARKERS,
            )
            >= 2
        )

    @staticmethod
    def should_include_general_information(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> bool:
        if path_contains_terms(base_path, GENERAL_INFORMATION_PATH_MARKERS):
            return True
        if CertificateInclusionPolicy._looks_like_test_results(context):
            return False
        if CertificateInclusionPolicy.looks_like_identification_table(context):
            return False
        return context.content_contains_any(CERTIFICATE_GENERAL_INFORMATION_MARKERS)

    @staticmethod
    def should_include_particulars(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> bool:
        if CertificateInclusionPolicy._looks_like_test_results(context):
            return False
        if path_contains_terms(base_path, PARTICULARS_PATH_MARKERS):
            return True
        if CertificateInclusionPolicy.looks_like_identification_table(context):
            return True
        return context.content_contains_any(CERTIFICATE_PARTICULARS_MARKERS)

    @staticmethod
    def should_include_compliance_information(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> bool:
        if CertificateInclusionPolicy._looks_like_test_results(context):
            return False
        if path_contains_terms(base_path, COMPLIANCE_INFORMATION_PATH_MARKERS):
            return True
        return context.content_contains_any(CERTIFICATE_COMPLIANCE_INFORMATION_MARKERS)

    @staticmethod
    def should_include_approval_information(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> bool:
        if CertificateInclusionPolicy._looks_like_test_results(context):
            return False
        if path_contains_terms(base_path, APPROVAL_INFORMATION_PATH_MARKERS):
            return True
        return context.content_contains_any(CERTIFICATE_APPROVAL_INFORMATION_MARKERS)

    @staticmethod
    def should_include_test_data(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> bool:
        if path_contains_terms(base_path, TEST_DATA_PATH_MARKERS):
            return True
        return context.content_contains_any(CERTIFICATE_TEST_DATA_MARKERS)

    @staticmethod
    def should_include_attachment_information(
        *,
        context: StructuredFamilyContext,
        base_path: list[str],
    ) -> bool:
        if path_contains_terms(base_path, ATTACHMENT_INFORMATION_PATH_MARKERS):
            return True
        return (
            CertificateInclusionPolicy._count_present_markers(
                context,
                CERTIFICATE_ATTACHMENT_INFORMATION_MARKERS,
            )
            >= 2
        )

    @staticmethod
    def looks_like_identification_table(
        context: StructuredFamilyContext,
    ) -> bool:
        return (
            CertificateInclusionPolicy._count_present_markers(
                context,
                IDENTIFICATION_TABLE_MARKERS,
            )
            >= 2
        )

    @staticmethod
    def _looks_like_test_results(
        context: StructuredFamilyContext,
    ) -> bool:
        return (
            path_contains_terms(
                context.base_section_path(),
                TEST_DATA_PATH_MARKERS,
            )
            or CertificateInclusionPolicy._count_present_markers(
                context,
                CERTIFICATE_TEST_DATA_MARKERS,
            )
            >= 2
        )

    @staticmethod
    def _count_present_markers(
        context: StructuredFamilyContext,
        markers: tuple[EvidenceMarker, ...],
    ) -> int:
        matches = _MARKER_MATCHER.find_matches(
            context.combined_text,
            markers,
        )

        return len(
            {
                match.marker
                for match in matches
            }
        )
