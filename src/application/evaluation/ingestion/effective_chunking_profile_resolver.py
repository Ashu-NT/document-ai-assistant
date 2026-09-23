from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.policies.document_chunking_policy_resolver import (
    DOCUMENT_TYPE_CHUNKING_PROFILES,
)
from src.application.workflows.parsing.builders.chunking.policies.policy.chunking_policy_registry import (
    default_registry,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.structural_profile_inference_cache import (
    load_structural_profile_inference,
)
from src.application.workflows.parsing.builders.document_graph.document_metadata.document_type_signal_cache import (
    load_document_type_confirmed,
)
from src.domain.document.entities.document import Document
from src.shared.exceptions import SchemaValidationError


@dataclass(slots=True, frozen=True)
class EffectiveChunkingProfileResolution:
    """The chunking profile/budget that actually produced this document's
    chunks - resolved the same way production resolved it, never guessed.

    `resolved=False` means neither of the two authoritative signals
    production itself records was available; callers must treat this as an
    explicit "cannot check" state, never silently substitute an unrelated
    ceiling (e.g. some other profile's budget, or a cross-profile max).
    """

    resolved: bool
    profile: ChunkingProfile | None = None
    max_chunk_tokens: int | None = None
    unresolved_reason: str | None = None


def resolve_effective_chunking_profile(
    document: Document,
) -> EffectiveChunkingProfileResolution:
    """Determines the ChunkingProfile that actually governed this document's
    chunk building, using only the same authoritative signals production
    itself persisted - never re-inferring structure independently and never
    falling back to a maximum-across-all-profiles ceiling.

    Two signals, tried in the same priority order the real chunking
    pipeline itself uses:

    1. `structural_profile_inference` (DocumentGraphBuilder persists this
       via `store_structural_profile_inference` whenever structural
       inference actually ran to pick a profile - the common case today,
       since nothing currently marks a document_type as confirmed).
    2. A confirmed `document_type` (`load_document_type_confirmed`) whose
       DocumentType maps to a known ChunkingProfile via the same
       `DOCUMENT_TYPE_CHUNKING_PROFILES` table
       `DocumentChunkingPolicyResolver` itself uses to make that exact
       decision when structural inference is skipped.

    If neither signal is present, resolution is explicitly unresolved -
    the caller must not substitute any other ceiling.
    """
    inference = load_structural_profile_inference(document.metadata)
    if inference is not None:
        return _resolve_budget_for_profile(inference.selected_profile)

    if load_document_type_confirmed(document.metadata):
        mapped_profile = DOCUMENT_TYPE_CHUNKING_PROFILES.get(document.document_type)
        if mapped_profile is not None:
            return _resolve_budget_for_profile(mapped_profile)
        return EffectiveChunkingProfileResolution(
            resolved=False,
            unresolved_reason=(
                "document_type is confirmed but "
                f"{document.document_type!r} has no known chunking profile mapping"
            ),
        )

    return EffectiveChunkingProfileResolution(
        resolved=False,
        unresolved_reason=(
            "neither structural_profile_inference nor a confirmed "
            "document_type is recorded in document.metadata"
        ),
    )


def _resolve_budget_for_profile(
    profile: ChunkingProfile,
) -> EffectiveChunkingProfileResolution:
    try:
        policy = default_registry().get(profile)
    except SchemaValidationError as exc:
        return EffectiveChunkingProfileResolution(
            resolved=False,
            profile=profile,
            unresolved_reason=(
                f"chunking policy for profile {profile.value!r} could not be "
                f"loaded: {exc}"
            ),
        )
    return EffectiveChunkingProfileResolution(
        resolved=True,
        profile=profile,
        max_chunk_tokens=policy.max_chunk_tokens,
    )


__all__ = [
    "EffectiveChunkingProfileResolution",
    "resolve_effective_chunking_profile",
]
