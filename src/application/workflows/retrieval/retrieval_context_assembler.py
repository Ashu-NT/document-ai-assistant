from dataclasses import dataclass

from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.domain.document import DocumentChunk
from src.domain.retrieval import RetrievedChunk


@dataclass(slots=True, frozen=True)
class RetrievalContextCandidate:
    anchor_chunk: RetrievedChunk
    document_chunk: DocumentChunk
    relation: str
    distance: int
    priority: int


def _default_token_budget() -> int:
    try:
        from src.config.settings import retrieval_settings
        return retrieval_settings.context_token_budget
    except Exception:
        return 900


class RetrievalContextAssembler:
    def __init__(self, *, token_budget: int | None = None) -> None:
        self.token_budget = max(
            1,
            token_budget if token_budget is not None else _default_token_budget(),
        )

    def assemble(
        self,
        *,
        anchors: list[RetrievedChunk],
        candidates_by_anchor_id: dict[str, list[RetrievalContextCandidate]],
        max_context_chunks: int,
        query_intent: RetrievalQueryIntent,
        to_retrieved_chunk,
    ) -> list[RetrievedChunk]:
        max_result_count = max(len(anchors), max_context_chunks)
        expanded: list[RetrievedChunk] = []
        seen: set[str] = set()
        token_total = 0

        for anchor in anchors:
            if anchor.chunk_id in seen:
                continue
            expanded.append(anchor)
            seen.add(anchor.chunk_id)
            token_total += self._estimate_retrieved_chunk_tokens(anchor)

        for anchor in anchors:
            if len(expanded) >= max_result_count:
                break

            candidates = candidates_by_anchor_id.get(anchor.chunk_id, [])
            grouped = self._group_candidates_by_relation(candidates)

            for relation in self._relation_order(query_intent, grouped):
                for candidate in grouped.get(relation, []):
                    chunk_id = candidate.document_chunk.chunk_id
                    if chunk_id in seen:
                        continue
                    if len(expanded) >= max_result_count:
                        break

                    candidate_tokens = self._estimate_document_chunk_tokens(
                        candidate.document_chunk
                    )
                    if token_total + candidate_tokens > self.token_budget:
                        continue

                    expanded.append(to_retrieved_chunk(candidate))
                    seen.add(chunk_id)
                    token_total += candidate_tokens

                if len(expanded) >= max_result_count:
                    break

        return expanded

    @staticmethod
    def _group_candidates_by_relation(
        candidates: list[RetrievalContextCandidate],
    ) -> dict[str, list[RetrievalContextCandidate]]:
        grouped: dict[str, list[RetrievalContextCandidate]] = {}

        for candidate in candidates:
            grouped.setdefault(candidate.relation, []).append(candidate)

        for relation_candidates in grouped.values():
            relation_candidates.sort(
                key=lambda candidate: (
                    -candidate.priority,
                    candidate.distance,
                    candidate.document_chunk.sequence_number,
                )
            )

        return grouped

    @staticmethod
    def _relation_order(
        query_intent: RetrievalQueryIntent,
        grouped_candidates: dict[str, list[RetrievalContextCandidate]],
    ) -> list[str]:
        ordered = ["same_section_part"]

        if query_intent in {
            RetrievalQueryIntent.OVERVIEW,
            RetrievalQueryIntent.PROCEDURE,
            RetrievalQueryIntent.SAFETY,
            RetrievalQueryIntent.TROUBLESHOOTING,
        }:
            ordered.extend(
                [
                    "ancestor_overview",
                    "descendant_detail",
                    "sibling_section",
                    "asset_companion",
                ]
            )

        if query_intent == RetrievalQueryIntent.IDENTIFIER:
            ordered.extend(
                [
                    "asset_companion",
                    "ancestor_overview",
                    "sibling_section",
                ]
            )

        if query_intent in {
            RetrievalQueryIntent.TABLE,
            RetrievalQueryIntent.FIGURE,
            RetrievalQueryIntent.SPECIFICATION,
        }:
            ordered.append("asset_companion")

        ordered.extend(
            [
                "asset_companion",
                "ancestor_overview",
                "descendant_detail",
                "sibling_section",
                "neighbor",
            ]
        )

        result: list[str] = []
        for relation in ordered:
            if relation in grouped_candidates and relation not in result:
                result.append(relation)

        for relation in grouped_candidates:
            if relation not in result:
                result.append(relation)

        return result

    @staticmethod
    def _estimate_retrieved_chunk_tokens(chunk: RetrievedChunk) -> int:
        return max(1, len(chunk.content.split()))

    @staticmethod
    def _estimate_document_chunk_tokens(chunk: DocumentChunk) -> int:
        if chunk.statistics is not None and chunk.statistics.token_count_estimate:
            return max(1, chunk.statistics.token_count_estimate)
        return max(1, len(chunk.content.split()))
