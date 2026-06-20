from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.document_chunking_policy_resolver import (
    DocumentChunkingPolicyResolver,
)
from src.domain.common import DocumentType


def test_resolver_uses_enum_profile_for_explicit_document_type() -> None:
    resolver = DocumentChunkingPolicyResolver()

    policy = resolver.resolve(
        document_title="Field Service Manual",
        document_type=DocumentType.MANUAL,
        sections=[],
        section_elements_by_id={},
    )

    assert policy.profile_name == ChunkingProfile.MANUAL
    assert policy.max_chunk_tokens == 240


def test_resolver_uses_profile_override_before_document_type() -> None:
    resolver = DocumentChunkingPolicyResolver()

    policy = resolver.resolve(
        document_title="Field Service Manual",
        document_type=DocumentType.MANUAL,
        sections=[],
        section_elements_by_id={},
        chunking_profile_override=ChunkingProfile.DEFAULT,
    )

    assert policy.profile_name == ChunkingProfile.DEFAULT
