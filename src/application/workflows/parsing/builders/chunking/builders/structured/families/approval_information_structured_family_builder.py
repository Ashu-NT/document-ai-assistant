from src.application.workflows.parsing.builders.chunking.builders.structured.family_builder_utils import (
    extend_markers,
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

from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerStrength,
)

_APPROVAL_INFORMATION_MARKERS = (
    EvidenceMarker(
        "approval",
        MarkerStrength.MEDIUM,
    ),
    EvidenceMarker(
        "basic specifications",
        MarkerStrength.MEDIUM,
    ),
    EvidenceMarker(
        "extended order code",
        MarkerStrength.STRONG,
    ),
    EvidenceMarker(
        "atex",
        MarkerStrength.STRONG,
    ),
    EvidenceMarker(
        "iecex",
        MarkerStrength.STRONG,
    ),
    EvidenceMarker(
        "conformity",
        MarkerStrength.MEDIUM,
    ),
)


class ApprovalInformationStructuredFamilyBuilder:
    def build(
        self,
        *,
        context: StructuredFamilyContext,
        marker_tuning: StructuredFamilyMarkerTuning | None,
    ) -> StructuredFamilySpecSelection:
        if context.matches_document_type(DocumentType.CERTIFICATE):
            return StructuredFamilySpecSelection()
        if not context.local_contains_any(_APPROVAL_INFORMATION_MARKERS):
            return StructuredFamilySpecSelection()

        return StructuredFamilySpecSelection(
            specs=[
                StructuredSectionWindowSpec(
                    family=StructuredEvidenceFamily.APPROVAL_INFORMATION,
                    section_path=self._approval_section_path(context),
                    anchor_markers=extend_markers(
                        family=StructuredEvidenceFamily.APPROVAL_INFORMATION,
                        base_markers=_APPROVAL_INFORMATION_MARKERS,
                        marker_tuning=marker_tuning,
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=0,
                    radius_after=2,
                    combine_all_windows=True,
                )
            ]
        )

    @staticmethod
    def _approval_section_path(
        context: StructuredFamilyContext,
    ) -> list[str]:
        path: list[str] = []
        for part in context.section.section_path:
            normalized = ApprovalInformationStructuredFamilyBuilder._normalize(part)
            if "safety" in normalized and not path:
                path.append(str(part))

        current_title = str(context.section.title or "").strip()
        if current_title:
            path.append(current_title)

        if (
            context.section_contains_any_term(("basic specifications",))
            or "extended order code" in ApprovalInformationStructuredFamilyBuilder._normalize(
                current_title
            )
        ):
            path.append("Basic specifications")
        else:
            path.append("Approval information")
        return path

    @staticmethod
    def _normalize(value: str | None) -> str:
        return " ".join(str(value or "").strip().lower().split())
