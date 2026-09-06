from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates.heading_candidate_assessment import (
    HeadingCandidateAssessment,
)
from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates.heading_candidate_document_context import (
    HeadingCandidateDocumentContext,
)
from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates.heading_candidate_role import (
    HeadingCandidateRole,
)
from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates.heading_candidate_scorer import (
    HeadingCandidateScorer,
)
from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates.heading_candidate_signal_extractor import (
    HeadingCandidateSignalExtractor,
)
from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    numbering_depth,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)


class HeadingCandidateRoleResolver:
    def __init__(
        self,
        *,
        signal_extractor: HeadingCandidateSignalExtractor | None = None,
        scorer: HeadingCandidateScorer | None = None,
    ) -> None:
        self.signal_extractor = signal_extractor or HeadingCandidateSignalExtractor()
        self.scorer = scorer or HeadingCandidateScorer()

    def resolve(
        self,
        *,
        headers: list[ParsedCanonicalElement],
        elements: list[ParsedCanonicalElement],
        hierarchy_resolution,
    ) -> dict[str, HeadingCandidateAssessment]:
        context = HeadingCandidateDocumentContext.build(
            headers=headers,
            elements=elements,
            toc_outline=hierarchy_resolution.toc_outline,
            numberings=hierarchy_resolution.header_numberings,
        )
        assessments: dict[str, HeadingCandidateAssessment] = {}
        active_header: ParsedCanonicalElement | None = None
        active_numberings: dict[int, str] = {}

        for index, header in enumerate(context.headers):
            assessment = self.scorer.assess(
                self.signal_extractor.extract(
                    context=context,
                    header_index=index,
                    active_header=active_header,
                    active_numberings=active_numberings,
                )
            )
            assessments[header.element_id] = assessment
            header.metadata["heading_candidate_role"] = assessment.role.value
            header.metadata["heading_candidate_confidence"] = assessment.confidence
            header.metadata["heading_candidate_reasons"] = list(assessment.reasons)
            if assessment.role != HeadingCandidateRole.OUTLINE_SECTION:
                continue

            active_header = header
            numbering = context.numbering_for(header)
            depth = numbering_depth(numbering)
            if numbering is None or depth is None:
                continue
            active_numberings[depth] = numbering
            for candidate_depth in tuple(active_numberings):
                if candidate_depth > depth:
                    active_numberings.pop(candidate_depth, None)

        return assessments
