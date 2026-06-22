from src.application.workflows.parsing.builders.chunking.builders.structured.families import (
    ApprovalInformationStructuredFamilyBuilder,
    CertificateStructuredFamilyBuilder,
    DatasheetStructuredFamilyBuilder,
    DrawingStructuredFamilyBuilder,
    ManualStructuredFamilyBuilder,
    ReportStructuredFamilyBuilder,
    SensorListStructuredFamilyBuilder,
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
from src.application.workflows.parsing.builders.chunking.builders.structured.tuning import (
    BenchmarkStructuredFamilyMarkerTuning,
)
from src.domain.common import DocumentType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


class StructuredFamilySpecFactory:
    def __init__(
        self,
        *,
        family_builders: list[object] | None = None,
        marker_tuning: StructuredFamilyMarkerTuning | None = None,
        enable_benchmark_tuning: bool = True,
    ) -> None:
        self.family_builders = family_builders or [
            DrawingStructuredFamilyBuilder(),
            CertificateStructuredFamilyBuilder(),
            DatasheetStructuredFamilyBuilder(),
            ReportStructuredFamilyBuilder(),
            ManualStructuredFamilyBuilder(),
            SensorListStructuredFamilyBuilder(),
            ApprovalInformationStructuredFamilyBuilder(),
        ]
        self.marker_tuning = (
            marker_tuning
            if marker_tuning is not None
            else (
                BenchmarkStructuredFamilyMarkerTuning()
                if enable_benchmark_tuning
                else None
            )
        )

    def build(
        self,
        *,
        document_title: str | None,
        document_type: DocumentType | None,
        section: DocumentSection,
        elements: list[CanonicalElement],
        normalizer,
        document_sections_combined_text: str = "",
    ) -> StructuredFamilySpecSelection:
        context = StructuredFamilyContext.from_inputs(
            document_title=document_title,
            document_type=document_type,
            section=section,
            elements=elements,
            normalizer=normalizer,
            document_sections_combined_text=document_sections_combined_text,
        )
        selections = [
            builder.build(
                context=context,
                marker_tuning=self.marker_tuning,
            )
            for builder in self.family_builders
        ]
        return StructuredFamilySpecSelection(
            specs=self._merge_specs(selections),
            consume_all_elements=any(
                selection.consume_all_elements
                for selection in selections
            ),
        )

    @staticmethod
    def _merge_specs(
        selections: list[StructuredFamilySpecSelection],
    ) -> list[StructuredSectionWindowSpec]:
        merged: dict[
            tuple[object, ...],
            StructuredSectionWindowSpec,
        ] = {}

        for selection in selections:
            for spec in selection.specs:
                key = (
                    spec.family,
                    tuple(spec.section_path),
                    spec.chunk_type,
                    spec.radius_before,
                    spec.radius_after,
                    spec.min_tokens,
                    spec.combine_all_windows,
                )
                existing = merged.get(key)
                if existing is None:
                    merged[key] = spec
                    continue

                merged[key] = StructuredSectionWindowSpec(
                    family=spec.family,
                    section_path=list(spec.section_path),
                    anchor_markers=tuple(
                        dict.fromkeys(
                            [*existing.anchor_markers, *spec.anchor_markers]
                        )
                    ),
                    chunk_type=spec.chunk_type,
                    radius_before=spec.radius_before,
                    radius_after=spec.radius_after,
                    min_tokens=spec.min_tokens,
                    combine_all_windows=spec.combine_all_windows,
                )

        return list(merged.values())
