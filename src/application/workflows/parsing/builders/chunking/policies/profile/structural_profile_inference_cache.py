from typing import Any

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

STRUCTURAL_PROFILE_INFERENCE_METADATA_KEY = "structural_profile_inference"


def store_structural_profile_inference(
    metadata: dict, inference: StructuralProfileInference
) -> None:
    metadata[STRUCTURAL_PROFILE_INFERENCE_METADATA_KEY] = _serialize(inference)


def load_structural_profile_inference(
    metadata: dict,
) -> StructuralProfileInference | None:
    raw = metadata.get(STRUCTURAL_PROFILE_INFERENCE_METADATA_KEY)
    if not isinstance(raw, dict):
        return None
    try:
        return _deserialize(raw)
    except (KeyError, ValueError, TypeError):
        # Cache written by an incompatible/older version of this schema --
        # fall back to recomputing rather than fail ingestion over it.
        return None


def _serialize(inference: StructuralProfileInference) -> dict[str, Any]:
    features = inference.features
    return {
        "selected_profile": inference.selected_profile.value,
        "confidence": inference.confidence,
        "scores": {
            profile.value: score for profile, score in inference.scores.items()
        },
        "reasons": {
            profile.value: list(reasons)
            for profile, reasons in inference.reasons.items()
        },
        "features": {
            "element_count": features.element_count,
            "section_count": features.section_count,
            "root_section_count": features.root_section_count,
            "nested_section_count": features.nested_section_count,
            "max_section_depth": features.max_section_depth,
            "text_element_count": features.text_element_count,
            "avg_text_tokens": features.avg_text_tokens,
            "table_ratio": features.table_ratio,
            "picture_ratio": features.picture_ratio,
            "list_ratio": features.list_ratio,
            "caption_ratio": features.caption_ratio,
            "nested_section_ratio": features.nested_section_ratio,
            "long_text_ratio": features.long_text_ratio,
            "short_text_ratio": features.short_text_ratio,
            "procedure_like_section_count": features.procedure_like_section_count,
            "evidence": {
                profile.value: {
                    "total_occurrences": summary.total_occurrences,
                    "distinct_term_count": summary.distinct_term_count,
                    "matching_title_count": summary.matching_title_count,
                    "matched_terms": list(summary.matched_terms),
                }
                for profile, summary in features.evidence.items()
            },
        },
    }


def _deserialize(raw: dict[str, Any]) -> StructuralProfileInference:
    raw_features = raw["features"]
    evidence = {
        ChunkingProfile(profile_value): StructuralEvidenceSummary(
            total_occurrences=summary["total_occurrences"],
            distinct_term_count=summary["distinct_term_count"],
            matching_title_count=summary["matching_title_count"],
            matched_terms=tuple(summary["matched_terms"]),
        )
        for profile_value, summary in raw_features["evidence"].items()
    }
    features = StructuralDocumentFeatures(
        element_count=raw_features["element_count"],
        section_count=raw_features["section_count"],
        root_section_count=raw_features["root_section_count"],
        nested_section_count=raw_features["nested_section_count"],
        max_section_depth=raw_features["max_section_depth"],
        text_element_count=raw_features["text_element_count"],
        avg_text_tokens=raw_features["avg_text_tokens"],
        table_ratio=raw_features["table_ratio"],
        picture_ratio=raw_features["picture_ratio"],
        list_ratio=raw_features["list_ratio"],
        caption_ratio=raw_features["caption_ratio"],
        nested_section_ratio=raw_features["nested_section_ratio"],
        long_text_ratio=raw_features["long_text_ratio"],
        short_text_ratio=raw_features["short_text_ratio"],
        evidence=evidence,
        procedure_like_section_count=raw_features["procedure_like_section_count"],
    )
    return StructuralProfileInference(
        selected_profile=ChunkingProfile(raw["selected_profile"]),
        confidence=raw["confidence"],
        scores={
            ChunkingProfile(profile_value): score
            for profile_value, score in raw["scores"].items()
        },
        reasons={
            ChunkingProfile(profile_value): list(reasons)
            for profile_value, reasons in raw["reasons"].items()
        },
        features=features,
    )
