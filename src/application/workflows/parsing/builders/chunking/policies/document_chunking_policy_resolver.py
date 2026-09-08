from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.policies.policy.chunking_policy_registry import (
    ChunkingPolicyRegistry,
    default_registry,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.structural_profile_inference import (
    StructuralProfileInference,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.structural_profile_inferer import (
    StructuralProfileInferer,
)
from src.application.workflows.parsing.builders.chunking.policies.policy.document_chunking_policy import (
    DocumentChunkingPolicy,
)
from src.domain.common import DocumentType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement

_DOCUMENT_TYPE_PROFILES: dict[DocumentType, ChunkingProfile] = {
    DocumentType.DATASHEET: ChunkingProfile.DATASHEET,
    DocumentType.DRAWING: ChunkingProfile.DRAWING,
    DocumentType.REPORT: ChunkingProfile.REPORT,
    DocumentType.MANUAL: ChunkingProfile.MANUAL,
    DocumentType.CERTIFICATE: ChunkingProfile.CERTIFICATE,
}


@dataclass(slots=True, frozen=True)
class ChunkingProfileResolution:
    profile: ChunkingProfile
    # Populated only when structural inference actually ran to produce
    # `profile` -- None when a confirmed document_type short-circuited it.
    structural_inference: StructuralProfileInference | None = None


@dataclass(slots=True, frozen=True)
class ResolvedChunkingPolicy:
    policy: DocumentChunkingPolicy
    structural_inference: StructuralProfileInference | None = None


class DocumentChunkingPolicyResolver:
    def __init__(
        self,
        *,
        profile_inferer: StructuralProfileInferer | None = None,
        policy_registry: ChunkingPolicyRegistry | None = None,
    ) -> None:
        self.profile_inferer = profile_inferer or StructuralProfileInferer()
        self._policy_registry = policy_registry or default_registry()

    def resolve(
        self,
        *,
        document_title: str | None,
        document_type: DocumentType | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
        chunking_profile_override: ChunkingProfile | None = None,
        document_type_confirmed: bool = True,
        precomputed_inference: StructuralProfileInference | None = None,
    ) -> ResolvedChunkingPolicy:
        if chunking_profile_override is not None:
            return ResolvedChunkingPolicy(
                policy=self._policy_registry.get(chunking_profile_override)
            )

        resolution = self.resolve_profile(
            document_title=document_title,
            document_type=document_type,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
            document_type_confirmed=document_type_confirmed,
            precomputed_inference=precomputed_inference,
        )
        return ResolvedChunkingPolicy(
            policy=self._policy_registry.get(resolution.profile),
            structural_inference=resolution.structural_inference,
        )

    def resolve_profile(
        self,
        *,
        document_title: str | None,
        document_type: DocumentType | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
        document_type_confirmed: bool = True,
        precomputed_inference: StructuralProfileInference | None = None,
    ) -> ChunkingProfileResolution:
        mapped_profile = (
            _DOCUMENT_TYPE_PROFILES.get(document_type)
            if document_type is not None
            else None
        )
        # A confirmed document_type (explicit metadata, not a title guess)
        # is trusted directly. An unconfirmed hint must still be
        # corroborated by structural inference -- see DocumentTypeHint.
        if mapped_profile is not None and document_type_confirmed:
            return ChunkingProfileResolution(profile=mapped_profile)

        if precomputed_inference is not None:
            return ChunkingProfileResolution(
                profile=precomputed_inference.selected_profile,
                structural_inference=precomputed_inference,
            )

        inference = self.profile_inferer.infer_result(
            document_title=document_title,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
        )
        return ChunkingProfileResolution(
            profile=inference.selected_profile,
            structural_inference=inference,
        )
