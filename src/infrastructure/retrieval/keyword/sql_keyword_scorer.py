import json
from dataclasses import dataclass

from src.application.workflows.retrieval.deduplication.retrieved_chunk_signature import (
    detect_chunk_role,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery
from src.infrastructure.db.orm_models import ChunkORM, DocumentORM
from src.infrastructure.retrieval.keyword.sql_keyword_query_terms import (
    normalize_query_text,
)

_STRUCTURED_TYPES = {
    ChunkType.SPARE_PARTS_TABLE.value,
    ChunkType.TECHNICAL_SPECIFICATION.value,
    ChunkType.CERTIFICATION_INFO.value,
    ChunkType.DRAWING_REFERENCE.value,
}
_PROCEDURE_TYPES = {
    ChunkType.OPERATION_INSTRUCTION.value,
    ChunkType.MAINTENANCE_PROCEDURE.value,
    ChunkType.MAINTENANCE_INTERVAL.value,
    ChunkType.TROUBLESHOOTING.value,
}
_NOISE_SECTION_TOKENS = {
    "environmentally",
    "responsible solutions",
    "engineered",
    "environmentally responsible solutions engineered",
    "table of contents",
    "revision / modification table",
}


@dataclass(slots=True, frozen=True)
class SqlKeywordScoreBreakdown:
    total_score: float
    metadata: dict[str, str]


class SqlKeywordScorer:
    def score(
        self,
        *,
        row: ChunkORM,
        document: DocumentORM | None,
        retrieval_query: RetrievalQuery | None,
        query_text: str,
        query_terms: list[str],
    ) -> SqlKeywordScoreBreakdown:
        query_identifiers = {
            identifier.lower()
            for identifier in (retrieval_query.detected_identifiers if retrieval_query else [])
            if identifier and identifier.strip()
        }
        section_path_parts = self._section_path_parts(row.section_path)
        section_path_text = " > ".join(section_path_parts)
        document_title = document.title if document is not None and document.title else ""
        file_name = document.file_name if document is not None else ""
        combined_text = " \n ".join(
            part
            for part in [
                row.content,
                row.embedding_text,
                section_path_text,
                document_title,
                file_name,
            ]
            if part
        )
        normalized_combined = normalize_query_text(combined_text)
        normalized_query = normalize_query_text(query_text)
        normalized_section_path = normalize_query_text(section_path_text)
        chunk_role = detect_chunk_role(row.content)

        exact_identifier_matches = sum(
            1
            for identifier in query_identifiers
            if identifier in combined_text.lower()
        )
        matched_terms = [
            term
            for term in query_terms
            if term in combined_text.lower()
        ]
        exact_phrase_match = bool(normalized_query and normalized_query in normalized_combined)
        ordered_match = self._ordered_query_match(
            normalized_combined=normalized_combined,
            query_terms=query_terms,
        )
        section_path_match = bool(
            query_terms
            and sum(1 for term in query_terms if term in normalized_section_path)
            >= min(2, len(query_terms))
        )
        chunk_type_fit = bool(
            retrieval_query is not None
            and retrieval_query.chunk_types
            and row.chunk_type in {
                chunk_type.value for chunk_type in retrieval_query.chunk_types
            }
        )
        structured_fit = (
            retrieval_query is not None
            and row.chunk_type in _STRUCTURED_TYPES
            and (
                retrieval_query.has_identifiers()
                or any(
                    marker in query_text.lower()
                    for marker in (
                        "spec",
                        "specification",
                        "table",
                        "parts list",
                        "certificate",
                        "approval",
                    )
                )
            )
        )

        score = 0.0
        score += exact_identifier_matches * 22.0
        if exact_identifier_matches > 0:
            score += 6.0
        if exact_phrase_match:
            score += max(8.0, len(query_terms) * 1.5)
        score += ordered_match
        score += len(matched_terms) * 1.35
        if section_path_match:
            score += 5.0
        if chunk_type_fit:
            score += 6.0
        if structured_fit:
            score += 4.0

        score -= self._chunk_role_penalty(chunk_role)
        score -= self._noise_penalty(
            section_path_text=section_path_text,
            content=row.content,
            query_text=query_text,
            exact_identifier_matches=exact_identifier_matches,
        )

        metadata = {
            "sql_keyword_source_score": f"{score:.6f}",
            "sql_exact_identifier_matches": str(exact_identifier_matches),
            "sql_exact_phrase_match": str(exact_phrase_match).lower(),
            "sql_section_path_match": str(section_path_match).lower(),
            "sql_ordered_match_bonus": f"{ordered_match:.6f}",
            "sql_chunk_role": chunk_role,
        }
        if document is not None:
            metadata["document_type"] = document.document_type

        return SqlKeywordScoreBreakdown(total_score=score, metadata=metadata)

    @staticmethod
    def _ordered_query_match(
        *,
        normalized_combined: str,
        query_terms: list[str],
    ) -> float:
        if len(query_terms) < 2:
            return 0.0

        haystack_tokens = normalized_combined.split()
        query_index = 0
        matched_positions: list[int] = []

        for index, token in enumerate(haystack_tokens):
            if token != query_terms[query_index]:
                continue
            matched_positions.append(index)
            query_index += 1
            if query_index == len(query_terms):
                break

        if query_index < 2:
            return 0.0
        if query_index == len(query_terms):
            span = matched_positions[-1] - matched_positions[0] + 1
            return 10.0 if span <= max(8, len(query_terms) * 2) else 7.0
        return float(query_index) * 1.5

    @staticmethod
    def _chunk_role_penalty(chunk_role: str) -> float:
        penalties = {
            "atomic_evidence": 0.0,
            "context_companion": 2.5,
            "asset_companion": 1.5,
            "overview_companion": 5.0,
        }
        return penalties.get(chunk_role, 0.0)

    def _noise_penalty(
        self,
        *,
        section_path_text: str,
        content: str,
        query_text: str,
        exact_identifier_matches: int,
    ) -> float:
        normalized_path = normalize_query_text(section_path_text)
        normalized_content = normalize_query_text(content)
        lowered_query = query_text.lower()

        penalty = 0.0
        if "table of contents" in normalized_path or self._looks_like_toc_content(content):
            penalty += 14.0
        if (
            "revision modification table" in normalized_path
            and "revision" not in lowered_query
            and "modification" not in lowered_query
        ):
            penalty += 12.0
        if exact_identifier_matches == 0 and any(
            token in normalized_path for token in _NOISE_SECTION_TOKENS
        ):
            penalty += 8.0
        if exact_identifier_matches == 0 and normalized_content.count("fundamentalmarinedevelopments") > 0:
            penalty += 4.0
        return penalty

    @staticmethod
    def _looks_like_toc_content(content: str) -> bool:
        lowered = (content or "").lower()
        return (
            "...." in lowered
            or ("table of contents" in lowered)
            or (".." in lowered and any(char.isdigit() for char in lowered))
        )

    @staticmethod
    def _section_path_parts(raw_section_path: str | None) -> list[str]:
        if not raw_section_path:
            return []
        try:
            loaded = json.loads(raw_section_path)
        except json.JSONDecodeError:
            return []
        if not isinstance(loaded, list):
            return []
        return [str(part) for part in loaded if str(part).strip()]
