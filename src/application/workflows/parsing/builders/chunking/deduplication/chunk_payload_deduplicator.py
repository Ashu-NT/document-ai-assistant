from src.application.workflows.parsing.builders.chunking.deduplication.chunk_payload_deduplication_result import (
    ChunkPayloadDeduplicationResult,
)
from src.application.workflows.parsing.builders.chunking.deduplication.chunk_payload_signature import (
    ChunkPayloadSignature,
)
from src.application.workflows.parsing.builders.chunking.deduplication.chunk_payload_similarity_policy import (
    ChunkPayloadSimilarityPolicy,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)
from src.domain.common import ChunkType


class ChunkPayloadDeduplicator:
    def __init__(
        self,
        *,
        similarity_policy: ChunkPayloadSimilarityPolicy | None = None,
    ) -> None:
        self.similarity_policy = similarity_policy or ChunkPayloadSimilarityPolicy()

    def deduplicate(
        self,
        payloads: list[ChunkPayload],
    ) -> ChunkPayloadDeduplicationResult:
        groups: list[dict[str, object]] = []

        for index, payload in enumerate(payloads):
            signature = ChunkPayloadSignature.from_payload(payload)
            matched_group: dict[str, object] | None = None
            matched_reason: str | None = None

            for group in groups:
                reason = self.similarity_policy.duplicate_reason(
                    left_payload=group["representative"],
                    left_signature=group["signature"],
                    right_payload=payload,
                    right_signature=signature,
                )
                if reason is None:
                    continue
                matched_group = group
                matched_reason = reason
                break

            if matched_group is None:
                groups.append(
                    {
                        "representative": payload,
                        "signature": signature,
                        "order_index": index,
                        "collapsed": [],
                        "reason": None,
                    }
                )
                continue

            representative = matched_group["representative"]
            representative_signature = matched_group["signature"]
            if self._is_better_representative(
                candidate=payload,
                candidate_signature=signature,
                existing=representative,
                existing_signature=representative_signature,
            ):
                matched_group["collapsed"].append(representative)
                matched_group["representative"] = payload
                matched_group["signature"] = signature
                matched_group["order_index"] = index
            else:
                matched_group["collapsed"].append(payload)

            matched_group["reason"] = matched_reason

        ordered_groups = sorted(
            groups,
            key=lambda group: int(group["order_index"]),
        )
        return ChunkPayloadDeduplicationResult(
            payloads=[
                group["representative"]
                for group in ordered_groups
            ],
            diagnostics=[
                self._diagnostic_for_group(group)
                for group in ordered_groups
                if group["collapsed"]
            ],
        )

    def _is_better_representative(
        self,
        *,
        candidate: ChunkPayload,
        candidate_signature: ChunkPayloadSignature,
        existing: ChunkPayload,
        existing_signature: ChunkPayloadSignature,
    ) -> bool:
        return self._representative_sort_key(
            candidate,
            candidate_signature,
        ) < self._representative_sort_key(
            existing,
            existing_signature,
        )

    @staticmethod
    def _representative_sort_key(
        payload: ChunkPayload,
        signature: ChunkPayloadSignature,
    ) -> tuple[int, int, int, int, int]:
        return (
            ChunkPayloadDeduplicator._category_rank(payload, signature),
            ChunkPayloadDeduplicator._semantic_priority_rank(payload),
            len(signature.stripped_token_set),
            payload.page_start or payload.page_end or 10**6,
            len(payload.content),
        )

    @staticmethod
    def _category_rank(
        payload: ChunkPayload,
        signature: ChunkPayloadSignature,
    ) -> int:
        if signature.role == "context_companion":
            return 4
        if signature.role == "overview_companion":
            return 5
        if signature.role == "asset_companion":
            return 6
        if payload.chunk_type == ChunkType.SPARE_PARTS_TABLE or signature.is_table_like:
            return 2
        if payload.chunk_type in {
            ChunkType.SAFETY_WARNING,
            ChunkType.MAINTENANCE_PROCEDURE,
            ChunkType.MAINTENANCE_INTERVAL,
            ChunkType.TROUBLESHOOTING,
            ChunkType.TECHNICAL_SPECIFICATION,
            ChunkType.INSTALLATION_INSTRUCTION,
            ChunkType.OPERATION_INSTRUCTION,
            ChunkType.CERTIFICATION_INFO,
        }:
            return 3
        return 1

    @staticmethod
    def _semantic_priority_rank(payload: ChunkPayload) -> int:
        if payload.chunk_type == ChunkType.SPARE_PARTS_TABLE:
            return 0
        if payload.chunk_type in {
            ChunkType.MAINTENANCE_INTERVAL,
            ChunkType.TROUBLESHOOTING,
        }:
            return 1
        if payload.chunk_type in {
            ChunkType.MAINTENANCE_PROCEDURE,
            ChunkType.INSTALLATION_INSTRUCTION,
            ChunkType.OPERATION_INSTRUCTION,
            ChunkType.SAFETY_WARNING,
        }:
            return 2
        if payload.chunk_type == ChunkType.TECHNICAL_SPECIFICATION:
            return 3
        if payload.chunk_type == ChunkType.CERTIFICATION_INFO:
            return 4
        if payload.chunk_type == ChunkType.OVERVIEW:
            return 6
        return 5

    @staticmethod
    def _diagnostic_for_group(group: dict[str, object]) -> dict[str, object]:
        representative = group["representative"]
        collapsed = group["collapsed"]
        return {
            "kept_section_path": list(representative.section_path),
            "collapsed_section_paths": [
                list(payload.section_path)
                for payload in collapsed
            ],
            "reason": group["reason"],
            "group_size": 1 + len(collapsed),
            "kept_preview": representative.content[:160],
            "collapsed_previews": [
                payload.content[:160]
                for payload in collapsed
            ],
        }
