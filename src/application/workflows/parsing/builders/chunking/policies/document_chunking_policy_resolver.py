from src.application.workflows.parsing.builders.chunking.policies.chunking_policy_registry import (
    ChunkingPolicyRegistry,
    default_registry,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_inferer import (
    ChunkingProfileInferer,
)
from src.application.workflows.parsing.builders.chunking.policies.document_chunking_policy import (
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


class DocumentChunkingPolicyResolver:
    def __init__(
        self,
        *,
        profile_inferer: ChunkingProfileInferer | None = None,
        policy_registry: ChunkingPolicyRegistry | None = None,
    ) -> None:
        self.profile_inferer = profile_inferer or ChunkingProfileInferer()
        self._policy_registry = policy_registry or default_registry()

    def resolve(
        self,
        *,
        document_title: str | None,
        document_type: DocumentType | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
        chunking_profile_override: ChunkingProfile | None = None,
    ) -> DocumentChunkingPolicy:
        if chunking_profile_override is not None:
            return self._policy_registry.get(chunking_profile_override)

        mapped_profile = (
            _DOCUMENT_TYPE_PROFILES.get(document_type)
            if document_type is not None
            else None
        )
        if mapped_profile is not None:
            return self._policy_registry.get(mapped_profile)

        profile = self.profile_inferer.infer(
            document_title=document_title,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
        )
        return self._policy_registry.get(profile)
