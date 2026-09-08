from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_document_features import (
    StructuralDocumentFeatures,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_evidence_matcher import (
    StructuralEvidenceSummary,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.structural_profile_inference import (
    StructuralProfileInference,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.structural_profile_inference_cache import (
    load_structural_profile_inference,
    store_structural_profile_inference,
)


def _sample_inference() -> StructuralProfileInference:
    features = StructuralDocumentFeatures(
        element_count=42,
        section_count=10,
        root_section_count=3,
        nested_section_count=7,
        max_section_depth=3,
        text_element_count=30,
        avg_text_tokens=12.5,
        table_ratio=0.1,
        picture_ratio=0.05,
        list_ratio=0.2,
        caption_ratio=0.02,
        nested_section_ratio=0.7,
        long_text_ratio=0.3,
        short_text_ratio=0.4,
        evidence={
            ChunkingProfile.MANUAL: StructuralEvidenceSummary(
                total_occurrences=5,
                distinct_term_count=3,
                matching_title_count=4,
                matched_terms=("maintenance", "procedure", "service"),
            ),
            ChunkingProfile.DATASHEET: StructuralEvidenceSummary(),
        },
        procedure_like_section_count=6,
    )
    return StructuralProfileInference(
        selected_profile=ChunkingProfile.MANUAL,
        confidence=0.82,
        scores={ChunkingProfile.MANUAL: 7.8, ChunkingProfile.DATASHEET: 2.1},
        reasons={ChunkingProfile.MANUAL: ["strong manual evidence"]},
        features=features,
    )


def test_store_then_load_round_trips_equivalent_inference() -> None:
    metadata: dict = {}
    original = _sample_inference()

    store_structural_profile_inference(metadata, original)
    loaded = load_structural_profile_inference(metadata)

    assert loaded is not None
    assert loaded.selected_profile == original.selected_profile
    assert loaded.confidence == original.confidence
    assert loaded.scores == original.scores
    assert loaded.reasons == original.reasons
    assert loaded.features == original.features


def test_load_returns_none_when_key_missing() -> None:
    assert load_structural_profile_inference({}) is None


def test_load_returns_none_for_malformed_cache_entry() -> None:
    metadata = {"structural_profile_inference": {"selected_profile": "manual"}}

    assert load_structural_profile_inference(metadata) is None
