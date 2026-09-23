from src.application.evaluation.ingestion.effective_chunking_profile_resolver import (
    resolve_effective_chunking_profile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_document_features import (
    StructuralDocumentFeatures,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.structural_profile_inference import (
    StructuralProfileInference,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.structural_profile_inference_cache import (
    store_structural_profile_inference,
)
from src.application.workflows.parsing.builders.document_graph.document_metadata.document_type_signal_cache import (
    store_document_type_confirmed,
)
from src.domain.common import DocumentType
from src.domain.document.entities.document import Document
from src.domain.document.value_objects import DocumentHashes


def _make_document(*, document_type: DocumentType = DocumentType.UNKNOWN) -> Document:
    return Document(
        document_id="doc_001",
        file_name="sample.pdf",
        file_path="sample.pdf",
        hashes=DocumentHashes(file_hash="h1", content_hash="c1"),
        document_type=document_type,
    )


def _make_inference(profile: ChunkingProfile) -> StructuralProfileInference:
    return StructuralProfileInference(
        selected_profile=profile,
        confidence=0.7,
        scores={profile: 0.7},
        reasons={profile: ["test"]},
        features=StructuralDocumentFeatures(),
    )


class TestStructuralInferencePriority:
    def test_uses_structural_inference_when_present(self) -> None:
        document = _make_document(document_type=DocumentType.UNKNOWN)
        store_structural_profile_inference(
            document.metadata, _make_inference(ChunkingProfile.DATASHEET)
        )

        resolution = resolve_effective_chunking_profile(document)

        assert resolution.resolved is True
        assert resolution.profile == ChunkingProfile.DATASHEET
        assert resolution.max_chunk_tokens == 270

    def test_structural_inference_wins_even_when_document_type_is_also_confirmed(
        self,
    ) -> None:
        # Priority order matters: structural_profile_inference is checked
        # FIRST, matching the same order the real chunking pipeline resolves
        # in (a confirmed document_type short-circuits structural inference
        # from running at all in production, so the two signals are never
        # actually in conflict in practice - but if both happen to be
        # present, this proves which one the resolver trusts).
        document = _make_document(document_type=DocumentType.MANUAL)
        store_document_type_confirmed(document.metadata, is_confirmed=True)
        store_structural_profile_inference(
            document.metadata, _make_inference(ChunkingProfile.CERTIFICATE)
        )

        resolution = resolve_effective_chunking_profile(document)

        assert resolution.profile == ChunkingProfile.CERTIFICATE


class TestConfirmedDocumentTypeFallback:
    def test_uses_confirmed_document_type_mapping_when_no_inference_present(self) -> None:
        document = _make_document(document_type=DocumentType.CERTIFICATE)
        store_document_type_confirmed(document.metadata, is_confirmed=True)

        resolution = resolve_effective_chunking_profile(document)

        assert resolution.resolved is True
        assert resolution.profile == ChunkingProfile.CERTIFICATE
        assert resolution.max_chunk_tokens == 250

    def test_confirmed_but_unmapped_document_type_is_unresolved(self) -> None:
        document = _make_document(document_type=DocumentType.UNKNOWN)
        store_document_type_confirmed(document.metadata, is_confirmed=True)

        resolution = resolve_effective_chunking_profile(document)

        assert resolution.resolved is False
        assert resolution.unresolved_reason is not None


class TestUnresolved:
    def test_not_confirmed_and_no_inference_is_unresolved(self) -> None:
        document = _make_document(document_type=DocumentType.MANUAL)
        store_document_type_confirmed(document.metadata, is_confirmed=False)

        resolution = resolve_effective_chunking_profile(document)

        assert resolution.resolved is False
        assert resolution.profile is None
        assert resolution.max_chunk_tokens is None
        assert resolution.unresolved_reason is not None

    def test_never_substitutes_an_unrelated_ceiling_when_unresolved(self) -> None:
        document = _make_document(document_type=DocumentType.MANUAL)
        store_document_type_confirmed(document.metadata, is_confirmed=False)

        resolution = resolve_effective_chunking_profile(document)

        # Explicit "cannot check" - never a number that looks like a real
        # budget (e.g. some other profile's ceiling, or a cross-profile max).
        assert resolution.max_chunk_tokens is None
