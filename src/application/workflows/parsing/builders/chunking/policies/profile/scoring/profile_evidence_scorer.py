from typing import Protocol

from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_document_features import (
    StructuralDocumentFeatures,
)


class ProfileEvidenceScorer(Protocol):
    """Scores how well StructuralDocumentFeatures support one ChunkingProfile.

    Each scorer covers exactly one profile and only reads shared features --
    never other scorers' results. ChunkingProfile.DEFAULT is not scored by
    any ProfileEvidenceScorer: whether the document is too ambiguous for a
    decisive profile is StructuralProfileDecisionPolicy's job, decided once
    every scorer here has already run.
    """

    profile: ChunkingProfile

    def score(self, features: StructuralDocumentFeatures) -> tuple[float, list[str]]:
        ...
