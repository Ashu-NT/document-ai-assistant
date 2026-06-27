import json
import re
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
_TABLE_QUERY_MARKERS = ("table", "spare part", "parts list", "part number", "order code")
_FIGURE_QUERY_MARKERS = ("figure", "diagram", "drawing", "schematic", "image", "label")
_OVERVIEW_QUERY_MARKERS = (
    "what does",
    "used for",
    "purpose",
    "function",
    "objective",
    "overview",
    "summary",
)
_OVERVIEW_SECTION_MARKERS = (
    "what it does",
    "overview",
    "introduction",
    "purpose",
    "function",
    "objective",
)

_ALNUM_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Morphological variant families for section-path matching only.
# Each family groups inflected forms that should be treated as equivalent when
# testing whether a query term appears in a section title/path.
_MORPH_FAMILIES: tuple[frozenset[str], ...] = (
    frozenset({"electrical", "electrically", "electric"}),
    frozenset({"connect", "connected", "connecting", "connection", "connections"}),
    frozenset({"calibrate", "calibrated", "calibrating", "calibration"}),
    frozenset({"lubricate", "lubricated", "lubricating", "lubrication"}),
    frozenset({"order", "ordered", "ordering"}),
    frozenset({"install", "installed", "installing", "installation"}),
    frozenset({"commission", "commissioned", "commissioning"}),
    # Singular / plural noun pairs — allow query "macerator" to match path "Macerators"
    frozenset({"macerator", "macerators"}),
    frozenset({"pump", "pumps"}),
    frozenset({"valve", "valves"}),
    frozenset({"component", "components"}),
    frozenset({"interval", "intervals"}),
    frozenset({"quantity", "quantities"}),
    frozenset({"procedure", "procedures"}),
    frozenset({"instruction", "instructions"}),
    frozenset({"specification", "specifications"}),
    # Verb stem / gerund / verbal-noun families
    frozenset({"remove", "removed", "removing", "removal"}),
    frozenset({"inspect", "inspected", "inspecting", "inspection"}),
    frozenset({"replace", "replaced", "replacing", "replacement"}),
    frozenset({"adjust", "adjusted", "adjusting", "adjustment"}),
    frozenset({"operate", "operated", "operating", "operation"}),
    # British / American spelling variants
    frozenset({"optimize", "optimise", "optimized", "optimised", "optimizing", "optimising"}),
    frozenset({"analyse", "analyze", "analysing", "analyzing", "analysis"}),
)
# Reverse lookup: term → all variants in its morphological family.
_MORPH_VARIANTS: dict[str, frozenset[str]] = {
    term: family for family in _MORPH_FAMILIES for term in family
}


def expand_query_terms_with_morph_variants(terms: list[str]) -> list[str]:
    """Return *terms* plus any morphological variants not already present.

    Used to widen SQL ILIKE candidate selection so that chunks whose text
    contains only an inflected form (e.g. "Removal" for query term "removed",
    or "Optimising" for "optimize") are retrieved as candidates before the
    scorer's morph logic fires.
    """
    seen: set[str] = set(terms)
    extra: list[str] = []
    for term in terms:
        for variant in _MORPH_VARIANTS.get(term, frozenset()):
            if variant not in seen:
                seen.add(variant)
                extra.append(variant)
    return terms + extra


def _compact_alnum(s: str) -> str:
    return "".join(_ALNUM_TOKEN_RE.findall(s.lower()))


def _contains_compact_id(compact_id: str, text: str) -> bool:
    """True if text contains compact_id after collapsing separators (hyphen/space/punctuation).

    Checks sliding windows of 1–3 consecutive alphanumeric tokens so that
    identifiers split by hyphens or spaces match their un-separated form and
    vice-versa (e.g. 'MK-311007' matches identifier 'MK311007').
    """
    if not compact_id or not text:
        return False
    tokens = _ALNUM_TOKEN_RE.findall(text.lower())
    for window in (1, 2, 3):
        for i in range(len(tokens) - window + 1):
            if "".join(tokens[i : i + window]) == compact_id:
                return True
    return False


def _section_path_hit(term: str, padded_path: str) -> bool:
    """True if *term* or any morphological variant appears as a whole word in *padded_path*."""
    if f" {term} " in padded_path:
        return True
    for variant in _MORPH_VARIANTS.get(term, frozenset()):
        if f" {variant} " in padded_path:
            return True
    return False


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
        # Compact identifiers so hyphenation/punctuation differences are ignored.
        query_identifiers_compact = {
            _compact_alnum(idf)
            for idf in (retrieval_query.detected_identifiers if retrieval_query else [])
            if idf and idf.strip()
        } - {""}  # drop empty strings produced by all-separator identifiers

        # --- Source separation ---
        content_text = " \n ".join(p for p in [row.content, row.embedding_text] if p)
        section_path_parts = self._section_path_parts(row.section_path)
        section_path_text = " > ".join(section_path_parts)
        document_title = document.title if document is not None and document.title else ""
        file_name = document.file_name if document is not None else ""
        document_text = " \n ".join(p for p in [document_title, file_name] if p)

        # Normalized forms (for term/phrase/ordered matching)
        normalized_content = normalize_query_text(content_text)
        normalized_section = normalize_query_text(section_path_text)
        normalized_query = normalize_query_text(query_text)
        lowered_query = query_text.lower()

        # Section split: local = last 1-2 parts; ancestor = rest
        local_parts, ancestor_parts = self._split_section_path(section_path_parts)
        normalized_local = normalize_query_text(" > ".join(local_parts))
        normalized_ancestor = normalize_query_text(" > ".join(ancestor_parts))

        chunk_role = detect_chunk_role(row.content)

        # --- Identifier matching (source-differentiated, evidence vs document-scope) ---
        # Identifiers that appear in the document title/filename label the entire document
        # rather than a specific chunk; they are "document-scope" and therefore less
        # discriminative.  Evidence identifiers (absent from the document name) carry much
        # stronger retrieval signal and receive higher boosts.
        document_scope_identifiers = {
            cid for cid in query_identifiers_compact
            if _contains_compact_id(cid, document_text)
        }
        # Each identifier is counted in the highest-priority source where it appears.
        content_identifier_matches = sum(
            1 for cid in query_identifiers_compact
            if _contains_compact_id(cid, content_text)
        )
        content_evidence_matches = sum(
            1 for cid in query_identifiers_compact
            if cid not in document_scope_identifiers
            and _contains_compact_id(cid, content_text)
        )
        content_docscope_matches = content_identifier_matches - content_evidence_matches
        section_identifier_matches = sum(
            1 for cid in query_identifiers_compact
            if not _contains_compact_id(cid, content_text)
            and _contains_compact_id(cid, section_path_text)
        )
        section_evidence_matches = sum(
            1 for cid in query_identifiers_compact
            if cid not in document_scope_identifiers
            and not _contains_compact_id(cid, content_text)
            and _contains_compact_id(cid, section_path_text)
        )
        section_docscope_matches = section_identifier_matches - section_evidence_matches
        document_identifier_matches = sum(
            1 for cid in query_identifiers_compact
            if not _contains_compact_id(cid, content_text)
            and not _contains_compact_id(cid, section_path_text)
            and _contains_compact_id(cid, document_text)
        )
        total_identifier_matches = (
            content_identifier_matches
            + section_identifier_matches
            + document_identifier_matches
        )
        # For noise-penalty logic: only meaningful if content/section carries the evidence
        meaningful_identifier_matches = content_identifier_matches + section_identifier_matches

        # --- Term matching (content only, normalized for punctuation robustness) ---
        matched_terms = [
            term for term in query_terms
            if term in normalized_content
        ]

        # --- Phrase / ordered matching (content only) ---
        exact_phrase_match = bool(normalized_query and normalized_query in normalized_content)
        ordered_match = self._ordered_query_match(
            normalized_combined=normalized_content,
            query_terms=query_terms,
        )

        # --- Section-path relevance (local >> ancestor) ---
        # Use whole-word matching so "do" does not falsely fire on "shutdown",
        # "macerator" does not match "macerators", etc.
        threshold = min(2, len(query_terms))
        padded_local = f" {normalized_local} "
        padded_ancestor = f" {normalized_ancestor} "
        local_term_hits = sum(1 for term in query_terms if _section_path_hit(term, padded_local))
        ancestor_term_hits = sum(1 for term in query_terms if _section_path_hit(term, padded_ancestor))
        local_section_match = bool(query_terms and local_term_hits >= threshold)
        ancestor_section_match = bool(
            query_terms
            and not local_section_match
            and ancestor_term_hits >= threshold
        )
        section_path_match = local_section_match or ancestor_section_match

        # --- Chunk-type fit ---
        chunk_type_fit = bool(
            retrieval_query is not None
            and retrieval_query.chunk_types
            and row.chunk_type in {
                chunk_type.value for chunk_type in retrieval_query.chunk_types
            }
        )
        # Extra bonus when the chunk is the most-preferred type for this intent.
        # This helps the best-fit type (e.g. TROUBLESHOOTING for a troubleshooting
        # query) outrank acceptable-but-secondary types (e.g. OPERATION_INSTRUCTION).
        primary_type_fit = (
            chunk_type_fit
            and retrieval_query is not None
            and bool(retrieval_query.chunk_types)
            and row.chunk_type == retrieval_query.chunk_types[0].value
        )
        structured_fit = (
            retrieval_query is not None
            and row.chunk_type in _STRUCTURED_TYPES
            and (
                retrieval_query.has_identifiers()
                or any(
                    marker in lowered_query
                    for marker in (
                        "spec",
                        "specification",
                        "table",
                        "parts list",
                        "certificate",
                        "approval",
                        "iecex",
                        "atex",
                    )
                )
            )
        )

        # --- Score assembly ---
        score = 0.0

        # Identifiers: evidence identifiers carry full signal; document-scope identifiers
        # (those present in the document name/title) receive reduced boosts because they
        # appear across most chunks and are therefore poor discriminators.
        score += content_evidence_matches * 22.0
        score += content_docscope_matches * 4.0
        score += section_evidence_matches * 10.0
        score += section_docscope_matches * 3.0
        score += document_identifier_matches * 2.0
        # Flat content-presence bonus: full for evidence matches, small for doc-scope.
        if content_evidence_matches > 0:
            score += 6.0
        elif content_docscope_matches > 0:
            score += 1.0

        # Phrase / ordered / term matching (content-only)
        if exact_phrase_match:
            score += max(8.0, len(query_terms) * 1.5)
        score += ordered_match
        score += len(matched_terms) * 1.35

        # Section-path: local subsection significantly more valuable than ancestor context
        if local_section_match:
            score += 5.0
            # Ancestor specificity tiebreaker: when local already matches, extra query
            # terms in ancestor path signal which sub-section is relevant (e.g. "macerator"
            # in ancestor "7.1 Macerators" discriminates against sibling "7.2 Food Waste
            # Press" even when both have the same local section title).
            if ancestor_term_hits > 0:
                score += ancestor_term_hits * self._ancestor_specificity_bonus(
                    chunk_type=row.chunk_type,
                    query_text=lowered_query,
                )
        elif ancestor_section_match:
            score += 1.5

        if any(marker in lowered_query for marker in _OVERVIEW_QUERY_MARKERS):
            score += self._overview_section_bonus(
                normalized_local=normalized_local,
                normalized_ancestor=normalized_ancestor,
            )

        if chunk_type_fit:
            score += 6.0
        if primary_type_fit:
            score += 3.0
        if structured_fit:
            score += 4.0

        score -= self._chunk_role_penalty(chunk_role)
        score -= self._noise_penalty(
            chunk_type=row.chunk_type,
            section_path_text=section_path_text,
            content=row.content,
            query_text=query_text,
            exact_identifier_matches=meaningful_identifier_matches,
        )

        # Conservative depth penalty: only kicks in for unusually deep paths.
        path_depth = len(section_path_parts)
        if path_depth > 8:
            score -= (path_depth - 8) * 0.7

        metadata = {
            "sql_keyword_source_score": f"{score:.6f}",
            "sql_exact_identifier_matches": str(total_identifier_matches),
            "sql_content_identifier_matches": str(content_identifier_matches),
            "sql_content_evidence_matches": str(content_evidence_matches),
            "sql_content_docscope_matches": str(content_docscope_matches),
            "sql_section_identifier_matches": str(section_identifier_matches),
            "sql_document_identifier_matches": str(document_identifier_matches),
            "sql_exact_phrase_match": str(exact_phrase_match).lower(),
            "sql_section_path_match": str(section_path_match).lower(),
            "sql_local_section_match": str(local_section_match).lower(),
            "sql_ordered_match_bonus": f"{ordered_match:.6f}",
            "sql_chunk_role": chunk_role,
            "sql_primary_type_fit": str(primary_type_fit).lower(),
        }
        if document is not None:
            metadata["document_type"] = document.document_type

        return SqlKeywordScoreBreakdown(total_score=score, metadata=metadata)

    @staticmethod
    def _split_section_path(
        parts: list[str],
    ) -> tuple[list[str], list[str]]:
        """Return (local, ancestor). Local = last 1-2 segments; ancestor = rest."""
        if len(parts) <= 2:
            return parts, []
        return parts[-2:], parts[:-2]

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

    @staticmethod
    def _ancestor_specificity_bonus(
        *,
        chunk_type: str,
        query_text: str,
    ) -> float:
        if chunk_type == ChunkType.MAINTENANCE_INTERVAL.value and any(
            marker in query_text
            for marker in ("maintenance", "interval", "lubrication", "service")
        ):
            return 2.5
        if any(marker in query_text for marker in _OVERVIEW_QUERY_MARKERS):
            return 2.0
        return 1.5

    @staticmethod
    def _overview_section_bonus(
        *,
        normalized_local: str,
        normalized_ancestor: str,
    ) -> float:
        if any(marker in normalized_local for marker in _OVERVIEW_SECTION_MARKERS):
            return 5.0
        if any(marker in normalized_ancestor for marker in _OVERVIEW_SECTION_MARKERS):
            return 2.0
        return 0.0

    def _noise_penalty(
        self,
        *,
        chunk_type: str,
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
        if exact_identifier_matches == 0 and chunk_type == ChunkType.SPARE_PARTS_TABLE.value:
            if not any(marker in lowered_query for marker in _TABLE_QUERY_MARKERS):
                penalty += 12.0
            if any(marker in lowered_query for marker in _OVERVIEW_QUERY_MARKERS):
                penalty += 6.0
        if exact_identifier_matches == 0 and chunk_type == ChunkType.DRAWING_REFERENCE.value:
            if not any(marker in lowered_query for marker in _FIGURE_QUERY_MARKERS):
                penalty += 8.0
        if exact_identifier_matches == 0 and chunk_type == ChunkType.TECHNICAL_SPECIFICATION.value:
            if any(marker in lowered_query for marker in _OVERVIEW_QUERY_MARKERS):
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
