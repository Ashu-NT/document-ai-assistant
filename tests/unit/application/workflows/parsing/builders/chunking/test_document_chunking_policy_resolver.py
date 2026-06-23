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
    assert policy.max_chunk_tokens == 1000


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


def test_resolver_uses_certificate_policy_for_certificate_document_type() -> None:
    resolver = DocumentChunkingPolicyResolver()

    policy = resolver.resolve(
        document_title="Inspection Certificate",
        document_type=DocumentType.CERTIFICATE,
        sections=[],
        section_elements_by_id={},
    )

    assert policy.profile_name == ChunkingProfile.CERTIFICATE
    assert policy.max_chunk_tokens == 500
    assert policy.include_table_context is True
    assert policy.include_picture_chunks is False


def test_resolver_maps_certificate_profile_override_to_certificate_policy() -> None:
    resolver = DocumentChunkingPolicyResolver()

    policy = resolver.resolve(
        document_title="Some Document",
        document_type=None,
        sections=[],
        section_elements_by_id={},
        chunking_profile_override=ChunkingProfile.CERTIFICATE,
    )

    assert policy.profile_name == ChunkingProfile.CERTIFICATE
    assert policy.max_chunk_tokens == 500


def test_resolver_drawing_policy_has_drawing_profile_name() -> None:
    resolver = DocumentChunkingPolicyResolver()

    policy = resolver.resolve(
        document_title="Wiring Diagram",
        document_type=DocumentType.DRAWING,
        sections=[],
        section_elements_by_id={},
    )

    assert policy.profile_name == ChunkingProfile.DRAWING
    assert policy.max_chunk_tokens == 300
