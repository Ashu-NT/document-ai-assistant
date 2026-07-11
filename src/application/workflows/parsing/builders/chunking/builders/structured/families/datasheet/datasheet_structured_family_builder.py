from src.application.workflows.parsing.builders.chunking.builders.structured.families.datasheet_family_helpers import (
    has_embedded_datasheet_signal,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.families.datasheet_window_specs import (
    build_datasheet_window_specs,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.family_builder_utils import (
    sanitized_base_path,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    DATASHEET_DOCUMENT_MARKERS,
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
from src.domain.common import DocumentType


class DatasheetStructuredFamilyBuilder:
    def build(
        self,
        *,
        context: StructuredFamilyContext,
        marker_tuning: StructuredFamilyMarkerTuning | None,
    ) -> StructuredFamilySpecSelection:
        if context.matches_document_type(DocumentType.DATASHEET):
            pass
        elif context.has_known_document_type():
            if not has_embedded_datasheet_signal(context):
                return StructuredFamilySpecSelection()
        elif not context.contains_any(DATASHEET_DOCUMENT_MARKERS):
            return StructuredFamilySpecSelection()

        base_path = sanitized_base_path(
            section_path=context.base_section_path(),
            section_title=context.section.title,
            document_title=context.document_title,
        )

        return StructuredFamilySpecSelection(
            specs=build_datasheet_window_specs(
                base_path=base_path,
                marker_tuning=marker_tuning,
            )
        )
