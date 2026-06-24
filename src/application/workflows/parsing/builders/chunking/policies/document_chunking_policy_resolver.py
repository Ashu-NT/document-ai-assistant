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
            return self._policy_for_profile(chunking_profile_override)

        if document_type == DocumentType.DATASHEET:
            return self._datasheet_policy()
        if document_type == DocumentType.DRAWING:
            return self._drawing_policy()
        if document_type == DocumentType.REPORT:
            return self._report_policy()
        if document_type == DocumentType.MANUAL:
            return self._manual_policy()
        if document_type == DocumentType.CERTIFICATE:
            return self._certificate_policy()

        profile = self.profile_inferer.infer(
            document_title=document_title,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
        )
        return self._policy_for_profile(profile)

    def _policy_for_profile(
        self,
        profile: ChunkingProfile,
    ) -> DocumentChunkingPolicy:
        yaml_policy = self._policy_registry.get(profile)
        if yaml_policy is not None:
            return yaml_policy

        if profile == ChunkingProfile.DATASHEET:
            return self._datasheet_policy()
        if profile == ChunkingProfile.CERTIFICATE:
            return self._certificate_policy()
        if profile == ChunkingProfile.DRAWING:
            return self._drawing_policy()
        if profile == ChunkingProfile.REPORT:
            return self._report_policy()
        if profile == ChunkingProfile.MANUAL:
            return self._manual_policy()

        return self._default_policy()

    @staticmethod
    def _manual_policy() -> DocumentChunkingPolicy:
        return DocumentChunkingPolicy(
            profile_name=ChunkingProfile.MANUAL,
            max_chunk_tokens=1000,
            chunk_overlap=100,
            same_topic_merge_tokens=120,
            intro_context_tokens=160,
            asset_context_window=2,
            asset_context_max_tokens=90,
            include_picture_chunks=True,
            include_table_context=True,
        )

    @staticmethod
    def _datasheet_policy() -> DocumentChunkingPolicy:
        return DocumentChunkingPolicy(
            profile_name=ChunkingProfile.DATASHEET,
            max_chunk_tokens=600,
            chunk_overlap=75,
            same_topic_merge_tokens=80,
            intro_context_tokens=110,
            asset_context_window=1,
            asset_context_max_tokens=60,
            include_picture_chunks=False,
            include_table_context=True,
        )

    @staticmethod
    def _drawing_policy() -> DocumentChunkingPolicy:
        return DocumentChunkingPolicy(
            profile_name=ChunkingProfile.DRAWING,
            max_chunk_tokens=300,
            chunk_overlap=35,
            same_topic_merge_tokens=60,
            intro_context_tokens=80,
            asset_context_window=1,
            asset_context_max_tokens=48,
            include_picture_chunks=True,
            include_table_context=False,
        )

    @staticmethod
    def _certificate_policy() -> DocumentChunkingPolicy:
        return DocumentChunkingPolicy(
            profile_name=ChunkingProfile.CERTIFICATE,
            max_chunk_tokens=500,
            chunk_overlap=60,
            same_topic_merge_tokens=80,
            intro_context_tokens=100,
            asset_context_window=1,
            asset_context_max_tokens=60,
            include_picture_chunks=False,
            include_table_context=True,
        )

    @staticmethod
    def _report_policy() -> DocumentChunkingPolicy:
        return DocumentChunkingPolicy(
            profile_name=ChunkingProfile.REPORT,
            max_chunk_tokens=800,
            chunk_overlap=100,
            same_topic_merge_tokens=100,
            intro_context_tokens=120,
            asset_context_window=1,
            asset_context_max_tokens=70,
            include_picture_chunks=True,
            include_table_context=True,
        )

    @staticmethod
    def _default_policy() -> DocumentChunkingPolicy:
        return DocumentChunkingPolicy(
            profile_name=ChunkingProfile.DEFAULT,
            max_chunk_tokens=200,
            chunk_overlap=20,
            same_topic_merge_tokens=90,
            intro_context_tokens=120,
            asset_context_window=1,
            asset_context_max_tokens=72,
            include_picture_chunks=True,
            include_table_context=True,
        )
