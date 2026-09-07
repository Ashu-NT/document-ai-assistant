from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_inference import (
    ChunkingProfileInference,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_scorer import (
    ChunkingProfileScorer,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_statistics_builder import (
    ChunkingProfileStatisticsBuilder,
)
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


class ChunkingProfileInferer:
    def __init__(
        self,
        *,
        statistics_builder: ChunkingProfileStatisticsBuilder | None = None,
        scorer: ChunkingProfileScorer | None = None,
    ) -> None:
        self.statistics_builder = (
            statistics_builder or ChunkingProfileStatisticsBuilder()
        )
        self.scorer = scorer or ChunkingProfileScorer()

    def infer(
        self,
        *,
        document_title: str | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
    ) -> ChunkingProfile:
        return self.infer_result(
            document_title=document_title,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
        ).selected_profile

    def infer_result(
        self,
        *,
        document_title: str | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
    ) -> ChunkingProfileInference:
        statistics = self.statistics_builder.build(
            document_title=document_title,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
        )
        return self.scorer.score(statistics)
