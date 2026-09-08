from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.document_chunking_policy_resolver import (
    DocumentChunkingPolicyResolver,
)
from src.domain.common import DocumentType
from src.domain.document import DocumentSection


def test_resolver_uses_enum_profile_for_explicit_document_type() -> None:
    resolver = DocumentChunkingPolicyResolver()

    policy = resolver.resolve(
        document_title="Field Service Manual",
        document_type=DocumentType.MANUAL,
        sections=[],
        section_elements_by_id={},
    ).policy

    assert policy.profile_name == ChunkingProfile.MANUAL
    assert policy.max_chunk_tokens == 310


def test_resolver_uses_profile_override_before_document_type() -> None:
    resolver = DocumentChunkingPolicyResolver()

    policy = resolver.resolve(
        document_title="Field Service Manual",
        document_type=DocumentType.MANUAL,
        sections=[],
        section_elements_by_id={},
        chunking_profile_override=ChunkingProfile.DEFAULT,
    ).policy

    assert policy.profile_name == ChunkingProfile.DEFAULT


def test_resolver_uses_certificate_policy_for_certificate_document_type() -> None:
    resolver = DocumentChunkingPolicyResolver()

    policy = resolver.resolve(
        document_title="Inspection Certificate",
        document_type=DocumentType.CERTIFICATE,
        sections=[],
        section_elements_by_id={},
    ).policy

    assert policy.profile_name == ChunkingProfile.CERTIFICATE
    assert policy.max_chunk_tokens == 250
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
    ).policy

    assert policy.profile_name == ChunkingProfile.CERTIFICATE
    assert policy.max_chunk_tokens == 250


def test_resolver_drawing_policy_has_drawing_profile_name() -> None:
    resolver = DocumentChunkingPolicyResolver()

    policy = resolver.resolve(
        document_title="Wiring Diagram",
        document_type=DocumentType.DRAWING,
        sections=[],
        section_elements_by_id={},
    ).policy

    assert policy.profile_name == ChunkingProfile.DRAWING
    assert policy.max_chunk_tokens == 300


def test_resolver_runs_structural_inference_for_unconfirmed_hint_even_when_mapped() -> None:
    """A title-derived hint (is_confirmed=False) must not short-circuit to
    the mapped profile the way a confirmed document_type does -- it has to
    be corroborated by structural inference, per DocumentTypeHint."""
    resolver = DocumentChunkingPolicyResolver()

    resolution = resolver.resolve_profile(
        document_title="Untitled",
        document_type=DocumentType.MANUAL,
        document_type_confirmed=False,
        sections=[],
        section_elements_by_id={},
    )

    assert resolution.structural_inference is not None


def test_resolver_confirmed_document_type_skips_structural_inference() -> None:
    resolver = DocumentChunkingPolicyResolver()

    resolution = resolver.resolve_profile(
        document_title="Field Service Manual",
        document_type=DocumentType.MANUAL,
        document_type_confirmed=True,
        sections=[],
        section_elements_by_id={},
    )

    assert resolution.profile == ChunkingProfile.MANUAL
    assert resolution.structural_inference is None


def test_resolver_reuses_precomputed_inference_instead_of_recomputing() -> None:
    resolver = DocumentChunkingPolicyResolver()

    first = resolver.resolve_profile(
        document_title="Untitled",
        document_type=None,
        sections=[],
        section_elements_by_id={},
    )
    assert first.structural_inference is not None

    reused = resolver.resolve_profile(
        document_title="Untitled",
        document_type=None,
        sections=[],
        section_elements_by_id={},
        precomputed_inference=first.structural_inference,
    )

    assert reused.structural_inference is first.structural_inference
    assert reused.profile == first.profile


def test_misleading_title_hint_loses_to_structural_evidence() -> None:
    """Title says 'Manual' (an unconfirmed hint), but the document's own
    section titles carry strong datasheet evidence and none of the manual
    evidence terms ("manual" itself isn't a manual-evidence term -- see
    StructuralEvidenceMatcher's term catalog). An unconfirmed hint must not
    override that real structural signal."""
    resolver = DocumentChunkingPolicyResolver()
    sections = [
        DocumentSection(
            section_id=f"sec_{i}",
            document_id="doc_1",
            title=title,
        )
        for i, title in enumerate(
            [
                "Technical Specifications",
                "Electrical Ratings",
                "Mechanical Dimensions",
                "Technical Data",
            ]
        )
    ]

    resolution = resolver.resolve_profile(
        document_title="Pump Manual",
        document_type=DocumentType.MANUAL,
        document_type_confirmed=False,
        sections=sections,
        section_elements_by_id={},
    )

    assert resolution.profile == ChunkingProfile.DATASHEET
    assert resolution.structural_inference is not None
