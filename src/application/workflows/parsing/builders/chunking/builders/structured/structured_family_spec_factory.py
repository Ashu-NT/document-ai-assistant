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
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_document_evidence_context import (
    StructuredDocumentEvidenceContext,
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
from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    StructuredMarkerMatcher,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.tuning import (
    BenchmarkStructuredFamilyMarkerTuning,
)
from src.domain.common import DocumentType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement
from src.application.workflows.parsing.profiling import GraphBuildProfiler


class StructuredFamilySpecFactory:
    def __init__(
        self,
        *,
        family_builders: list[object] | None = None,
        marker_tuning: StructuredFamilyMarkerTuning | None = None,
        enable_benchmark_tuning: bool = True,
        profiler: GraphBuildProfiler | None = None,
    ) -> None:
        self.profiler = profiler or GraphBuildProfiler.disabled()
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

    def set_profiler(self, profiler: GraphBuildProfiler | None) -> None:
        self.profiler = profiler or GraphBuildProfiler.disabled()

    def build(
        self,
        *,
        document_title: str | None,
        document_type: DocumentType | None,
        section: DocumentSection,
        elements: list[CanonicalElement],
        normalizer,
        document_sections_combined_text: str = "",
        document_context: StructuredDocumentEvidenceContext | None = None,
        marker_matcher: StructuredMarkerMatcher | None = None,
    ) -> StructuredFamilySpecSelection:
        marker_matcher = marker_matcher or StructuredMarkerMatcher()
        reused_document_context = document_context is not None
        document_context = document_context or StructuredDocumentEvidenceContext.build(
            document_title=document_title,
            document_sections_combined_text=document_sections_combined_text,
            matcher=marker_matcher,
        )
        with self.profiler.aggregate(
            name="structured_family_spec_factory.prepare_context",
            input_counts={
                "sections": 1,
                "elements": len(elements),
                "document_section_text_chars": len(
                    document_context.normalized_section_text
                ),
            },
        ) as stage:
            context = StructuredFamilyContext.from_inputs(
                document_title=document_title,
                document_type=document_type,
                section=section,
                elements=elements,
                normalizer=normalizer,
                document_context=document_context,
                matcher=marker_matcher,
            )
            stage.output_counts["normalized_elements"] = len(context.normalized_texts)
            stage.operations["document_context_reused"] = int(
                reused_document_context
            )

        with self.profiler.aggregate(
            name="structured_family_spec_factory.select_specs",
            input_counts={"sections": 1, "family_builders": len(self.family_builders)},
        ) as stage:
            selections = []
            for builder in self.family_builders:
                family_name = type(builder).__name__
                with self.profiler.aggregate(
                    name=(
                        "structured_family_spec_factory.select_specs."
                        f"{family_name}"
                    ),
                    input_counts={"sections": 1},
                ) as family_stage:
                    selection = builder.build(
                        context=context,
                        marker_tuning=self.marker_tuning,
                    )
                    family_stage.output_counts["specs"] = len(selection.specs)
                selections.append(selection)
            specs = self._merge_specs(selections)
            stage.output_counts["specs"] = len(specs)
            return StructuredFamilySpecSelection(specs=specs)

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
                    include_full_section_if_no_anchor=(
                        existing.include_full_section_if_no_anchor
                        or spec.include_full_section_if_no_anchor
                    ),
                    section_context_matches=(
                        existing.section_context_matches
                        or spec.section_context_matches
                    ),
                )

        return list(merged.values())
