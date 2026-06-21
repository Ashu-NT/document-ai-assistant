from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.deduplication.chunk_payload_signature import (
    ChunkPayloadSignature,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)


@dataclass(slots=True, frozen=True)
class ChunkPayloadSimilarityPolicy:
    exact_duplicate_enabled: bool = True
    context_companion_collapse_enabled: bool = True
    overview_duplicate_collapse_enabled: bool = True
    token_overlap_threshold: float = 0.90
    containment_threshold: float = 0.95
    min_unique_token_count: int = 20

    def duplicate_reason(
        self,
        *,
        left_payload: ChunkPayload,
        left_signature: ChunkPayloadSignature,
        right_payload: ChunkPayload,
        right_signature: ChunkPayloadSignature,
    ) -> str | None:
        if not self._paths_or_pages_related(left_payload, right_payload):
            return None

        if self._identifiers_conflict(left_signature, right_signature):
            return None

        if self._exact_duplicate(left_signature, right_signature):
            return "exact_normalized_content"

        if self._different_table_rows(left_signature, right_signature):
            return None

        context_reason = self._companion_duplicate_reason(
            companion_role="context_companion",
            left_signature=left_signature,
            right_signature=right_signature,
        )
        if context_reason is not None and self.context_companion_collapse_enabled:
            return context_reason

        overview_reason = self._overview_duplicate_reason(
            left_signature=left_signature,
            right_signature=right_signature,
        )
        if overview_reason is not None and self.overview_duplicate_collapse_enabled:
            return overview_reason

        if (
            left_signature.role != "atomic_evidence"
            or right_signature.role != "atomic_evidence"
        ):
            return None

        if self._is_high_containment_duplicate(left_signature, right_signature):
            return "high_containment_duplicate"

        return None

    def _companion_duplicate_reason(
        self,
        *,
        companion_role: str,
        left_signature: ChunkPayloadSignature,
        right_signature: ChunkPayloadSignature,
    ) -> str | None:
        companion_signature, atomic_signature = self._ordered_signatures(
            left_signature,
            right_signature,
            companion_role=companion_role,
        )
        if companion_signature is None or atomic_signature is None:
            return None

        if self._normalized_stripped_match(companion_signature, atomic_signature):
            return f"{companion_role}_duplicate"

        if self._is_high_containment_duplicate(
            companion_signature,
            atomic_signature,
        ):
            return f"{companion_role}_duplicate"

        return None

    def _overview_duplicate_reason(
        self,
        *,
        left_signature: ChunkPayloadSignature,
        right_signature: ChunkPayloadSignature,
    ) -> str | None:
        overview_signature, atomic_signature = self._ordered_signatures(
            left_signature,
            right_signature,
            companion_role="overview_companion",
        )
        if overview_signature is None or atomic_signature is None:
            return None

        if overview_signature.has_subsection_summary:
            return None

        if self._normalized_stripped_match(overview_signature, atomic_signature):
            return "overview_duplicate"

        if self._is_high_containment_duplicate(
            overview_signature,
            atomic_signature,
        ):
            return "overview_duplicate"

        return None

    def _exact_duplicate(
        self,
        left_signature: ChunkPayloadSignature,
        right_signature: ChunkPayloadSignature,
    ) -> bool:
        if not self.exact_duplicate_enabled:
            return False
        return (
            bool(left_signature.normalized_content)
            and left_signature.normalized_content == right_signature.normalized_content
        )

    @staticmethod
    def _different_table_rows(
        left_signature: ChunkPayloadSignature,
        right_signature: ChunkPayloadSignature,
    ) -> bool:
        if not left_signature.is_table_like or not right_signature.is_table_like:
            return False

        return (
            left_signature.normalized_stripped_content
            != right_signature.normalized_stripped_content
        )

    @staticmethod
    def _identifiers_conflict(
        left_signature: ChunkPayloadSignature,
        right_signature: ChunkPayloadSignature,
    ) -> bool:
        return (
            bool(left_signature.identifier_tokens)
            and bool(right_signature.identifier_tokens)
            and left_signature.identifier_tokens != right_signature.identifier_tokens
        )

    def _is_high_containment_duplicate(
        self,
        left_signature: ChunkPayloadSignature,
        right_signature: ChunkPayloadSignature,
    ) -> bool:
        left_tokens = left_signature.stripped_token_set
        right_tokens = right_signature.stripped_token_set
        if not left_tokens or not right_tokens:
            return False

        smaller_tokens, larger_tokens = sorted(
            (left_tokens, right_tokens),
            key=len,
        )
        overlap = len(smaller_tokens & larger_tokens)
        containment = overlap / len(smaller_tokens)
        unique_tokens = len(larger_tokens - smaller_tokens)

        return (
            containment >= self.containment_threshold
            and unique_tokens <= self.min_unique_token_count
        )

    @staticmethod
    def _normalized_stripped_match(
        left_signature: ChunkPayloadSignature,
        right_signature: ChunkPayloadSignature,
    ) -> bool:
        return (
            bool(left_signature.normalized_stripped_content)
            and left_signature.normalized_stripped_content
            == right_signature.normalized_stripped_content
        )

    @staticmethod
    def _ordered_signatures(
        left_signature: ChunkPayloadSignature,
        right_signature: ChunkPayloadSignature,
        *,
        companion_role: str,
    ) -> tuple[ChunkPayloadSignature | None, ChunkPayloadSignature | None]:
        if (
            left_signature.role == companion_role
            and right_signature.role == "atomic_evidence"
        ):
            return left_signature, right_signature
        if (
            right_signature.role == companion_role
            and left_signature.role == "atomic_evidence"
        ):
            return right_signature, left_signature
        return None, None

    @staticmethod
    def _paths_or_pages_related(
        left_payload: ChunkPayload,
        right_payload: ChunkPayload,
    ) -> bool:
        if left_payload.section_id and left_payload.section_id == right_payload.section_id:
            return True
        if left_payload.section_path == right_payload.section_path:
            return True
        if ChunkPayloadSimilarityPolicy._is_path_prefix(
            left_payload.section_path,
            right_payload.section_path,
        ) or ChunkPayloadSimilarityPolicy._is_path_prefix(
            right_payload.section_path,
            left_payload.section_path,
        ):
            return True
        return ChunkPayloadSimilarityPolicy._page_spans_overlap(
            left_payload.page_start,
            left_payload.page_end,
            right_payload.page_start,
            right_payload.page_end,
        )

    @staticmethod
    def _is_path_prefix(
        candidate_ancestor_path: list[str],
        candidate_descendant_path: list[str],
    ) -> bool:
        if not candidate_ancestor_path:
            return False
        if len(candidate_ancestor_path) > len(candidate_descendant_path):
            return False
        return (
            candidate_descendant_path[: len(candidate_ancestor_path)]
            == candidate_ancestor_path
        )

    @staticmethod
    def _page_spans_overlap(
        left_start: int | None,
        left_end: int | None,
        right_start: int | None,
        right_end: int | None,
    ) -> bool:
        resolved_left_start = left_start if left_start is not None else left_end
        resolved_left_end = left_end if left_end is not None else left_start
        resolved_right_start = right_start if right_start is not None else right_end
        resolved_right_end = right_end if right_end is not None else right_start

        if (
            resolved_left_start is None
            or resolved_left_end is None
            or resolved_right_start is None
            or resolved_right_end is None
        ):
            return False

        return not (
            resolved_left_end < resolved_right_start
            or resolved_right_end < resolved_left_start
        )
