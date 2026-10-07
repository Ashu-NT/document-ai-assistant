from __future__ import annotations

import re
from dataclasses import dataclass

from src.application.workflows.parsing.tables.rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    normalize_cell,
)
from src.application.workflows.shared.table_column_resolution_state import (
    ColumnResolutionState,
)
from src.application.workflows.shared.table_column_semantic_evidence import (
    ColumnSemanticEvidence,
    EvidenceCategory,
)
from src.application.workflows.shared.table_column_semantic_resolution import (
    ColumnSemanticResolution,
    TableColumnSemantics,
)
from src.application.workflows.shared.table_column_semantic_role import (
    TableColumnSemanticRole,
)
from src.domain.assets import TableAsset

# Shared, deterministic, application-level column semantic resolver -- a
# sibling to TableSemanticClassifier (which classifies a whole TABLE), not a
# replacement. Reuses that classifier's already-persisted outputs
# (table_category/table_category_confidence/table_shape/
# table_structure_quality/header_paths, all already fields on TableAsset) as
# CONTEXTUAL/STRUCTURAL evidence, and reuses TableRowCanonicalizer for the
# exact same header/row canonicalization TableSemanticClassifier itself uses.
#
# Deliberately NOT a first-match-wins alias lookup: every (column, role)
# evidence item is a weighted vote; a column resolves only when one role's
# combined support clears an absolute floor AND a margin over the runner-up.
# Header aliases below are WEAK LEXICAL evidence only, never automatic
# truth -- conflicting structural/content/relational evidence can, and in
# real tables does, prevent resolution (see the MTU "Task" column: literal
# header text votes `task`, but its structural label "Parameter" votes
# `label`, and relational pressure from a stronger `task`-column elsewhere
# suppresses the weaker one -- abstention, not an invented MTU-specific
# rule).
#
# `_LEXICAL_HEADER_ALIASES` below is intentionally a close copy of
# `question_answering.answer_context.tables.table_header_semantics.
# _HEADER_ROLE_ALIASES`'s DATA (not its matching logic). It is duplicated,
# not imported, because importing it would make this shared/generic module
# depend on the Q&A package -- exactly the inverted layering this module
# exists to avoid (shared core -> {Q&A adapter, extraction adapter}, never
# the reverse). Unlike the original, a header string here may resolve to
# MULTIPLE roles (see "item" below, which the original data already lists
# under both "label" and "position" -- the original's first-match-wins
# lookup silently hid that ambiguity; this classifier surfaces it instead).
_LEXICAL_HEADER_ALIASES: dict[str, tuple[str, ...]] = {
    "label": (
        "attribute",
        "characteristic",
        "data",
        "description",
        "designation",
        "field",
        "item",
        "parameter",
        "particular",
        "particulars",
        "property",
        "specification",
    ),
    "value": ("details", "rating", "result", "setting", "value"),
    "task": (
        "activity",
        "action",
        "inspection item",
        "maintenance item",
        "maintenance task",
        "operation",
        "task",
    ),
    "interval": (
        "frequency",
        "inspection interval",
        "interval",
        "period",
        "schedule",
        "service interval",
    ),
    "component": ("assembly", "component", "equipment", "location", "part", "system"),
    "notes": (
        "comment",
        "comments",
        "note",
        "notes",
        "reference",
        "remark",
        "remarks",
        "task reference",
    ),
    "position": (
        "item",
        "item no",
        "part pos",
        "pos",
        "pos.",
        "pos nr",
        "position",
        "position no",
    ),
    "quantity": ("qty", "quantity"),
    "unit": ("unit",),
    "part_no": (
        "article no",
        "material no",
        "order no",
        "part no",
        "part number",
        "spare part no",
    ),
    "service": ("function", "service", "service function"),
    "type": ("type",),
}

_HEADER_PUNCTUATION_PATTERN = re.compile(r"[.:;]+")
_LEADING_NUMERIC_PATTERN = re.compile(r"^[+-]?\d[\d,.\s]*")

_RICH_TEXT_SUPPORT = (TableColumnSemanticRole.TASK, TableColumnSemanticRole.NOTES)
_RICH_TEXT_OPPOSE = (
    TableColumnSemanticRole.VALUE,
    TableColumnSemanticRole.QUANTITY,
    TableColumnSemanticRole.UNIT,
    TableColumnSemanticRole.PART_NO,
    TableColumnSemanticRole.POSITION,
)
_NUMERIC_SUPPORT = (
    TableColumnSemanticRole.VALUE,
    TableColumnSemanticRole.QUANTITY,
    TableColumnSemanticRole.UNIT,
    TableColumnSemanticRole.INTERVAL,
)
_NUMERIC_OPPOSE = (
    TableColumnSemanticRole.TASK,
    TableColumnSemanticRole.NOTES,
    TableColumnSemanticRole.LABEL,
    TableColumnSemanticRole.COMPONENT,
    TableColumnSemanticRole.SERVICE,
)
_CODE_LIKE_SUPPORT = (
    TableColumnSemanticRole.PART_NO,
    TableColumnSemanticRole.POSITION,
    TableColumnSemanticRole.TYPE,
)


def _normalize_header_text(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    normalized = _HEADER_PUNCTUATION_PATTERN.sub(" ", normalized)
    return " ".join(normalized.split())


def _singularize_token(token: str) -> str:
    """Minimal, generic English plural stripping -- not vendor/domain
    specific. Exists so e.g. a real table's "Maintenance tasks" column
    header can match the same lexical evidence as "Maintenance task"
    without hand-listing every plural form in the alias data."""
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("ses") and len(token) > 4:
        return token[:-2]
    if token.endswith("s") and not token.endswith("ss") and len(token) > 3:
        return token[:-1]
    return token


def _singularized_header_text(normalized: str) -> str:
    return " ".join(_singularize_token(token) for token in normalized.split())


def _lookup_roles_by_text(text: str) -> list[TableColumnSemanticRole]:
    if not text:
        return []
    matches: list[TableColumnSemanticRole] = [
        role for role in TableColumnSemanticRole if text == role.value
    ]
    for role_value, aliases in _LEXICAL_HEADER_ALIASES.items():
        if text in aliases:
            role = TableColumnSemanticRole(role_value)
            if role not in matches:
                matches.append(role)
    return matches


def _looks_numeric_ish(value: str) -> bool:
    match = _LEADING_NUMERIC_PATTERN.match(value.strip())
    if match is None:
        return False
    digit_run = match.group(0)
    return sum(character.isdigit() for character in digit_run) >= 2


@dataclass(slots=True, frozen=True)
class _ColumnObservation:
    column_index: int
    source_header: str | None
    structural_header: str | None
    non_empty_cells: list[str]


class TableColumnSemanticClassifier:
    """Deterministic, on-demand column semantic resolver. No LLM, no
    embeddings, no persistence -- see `classify`."""

    VERSION = "table_column_semantic_classifier_v1"

    LEXICAL_EXACT_WEIGHT = 0.5
    LEXICAL_MORPHOLOGICAL_WEIGHT = 0.4
    STRUCTURAL_WEIGHT = 0.25
    CONTENT_STRONG_WEIGHT = 0.3
    CONTENT_OPPOSE_NUMERIC_WEIGHT = 0.2
    CONTENT_OPPOSE_TEXT_WEIGHT = 0.15
    CONTENT_WEAK_WEIGHT = 0.15
    RELATIONAL_SUPPRESSION_WEIGHT = 0.3
    RELATIONAL_SUPPRESSION_EPSILON = 1e-9
    CONTEXT_TRUST_THRESHOLD = 0.8
    CONTEXT_DAMPENING_WEIGHT = 0.1
    RESOLVE_FLOOR = 0.5
    AMBIGUOUS_MARGIN = 0.15
    PLAUSIBILITY_FLOOR = 0.25
    RICH_TEXT_AVG_TOKEN_THRESHOLD = 4.0
    CODE_LIKE_AVG_TOKEN_THRESHOLD = 1.5
    NUMERIC_FRACTION_THRESHOLD = 0.6

    def __init__(self, *, row_canonicalizer: TableRowCanonicalizer | None = None) -> None:
        self.row_canonicalizer = row_canonicalizer or TableRowCanonicalizer()

    def classify(self, table: TableAsset) -> TableColumnSemantics:
        observations = self._build_observations(table)
        if not observations:
            return TableColumnSemantics(
                table_id=table.table_id, columns=(), classifier_version=self.VERSION
            )

        evidence_by_column: dict[int, list[ColumnSemanticEvidence]] = {
            obs.column_index: [] for obs in observations
        }
        for obs in observations:
            evidence_by_column[obs.column_index].extend(self._lexical_evidence(obs))
            evidence_by_column[obs.column_index].extend(self._structural_evidence(obs))
            evidence_by_column[obs.column_index].extend(self._content_evidence(obs))

        raw_scores = {
            column_index: self._scores_from_evidence(items)
            for column_index, items in evidence_by_column.items()
        }
        relational_evidence, adjusted_scores = self._relational_pass(raw_scores)
        for column_index, items in relational_evidence.items():
            evidence_by_column[column_index].extend(items)

        context_evidence, final_scores = self._contextual_pass(table, adjusted_scores)
        for column_index, items in context_evidence.items():
            evidence_by_column[column_index].extend(items)

        resolutions = tuple(
            self._resolve_column(obs, evidence_by_column[obs.column_index], final_scores[obs.column_index])
            for obs in observations
        )
        return TableColumnSemantics(
            table_id=table.table_id, columns=resolutions, classifier_version=self.VERSION
        )

    # ---- observation building -------------------------------------------------

    def _build_observations(self, table: TableAsset) -> list[_ColumnObservation]:
        canonical_rows = self.row_canonicalizer.canonicalize(table.rows)
        if not canonical_rows:
            return []

        has_header_row = self.row_canonicalizer.has_explicit_header_row(canonical_rows)
        headers = canonical_rows[0] if has_header_row else []
        data_rows = canonical_rows[1:] if has_header_row else canonical_rows
        column_count = max((len(row) for row in canonical_rows), default=0)

        observations: list[_ColumnObservation] = []
        for column_index in range(column_count):
            source_header = (
                normalize_cell(headers[column_index])
                if column_index < len(headers)
                else None
            )
            source_header = source_header or None
            structural_header = self._structural_header(table, column_index)
            non_empty_cells = [
                normalize_cell(row[column_index])
                for row in data_rows
                if column_index < len(row) and normalize_cell(row[column_index])
            ]
            observations.append(
                _ColumnObservation(
                    column_index=column_index,
                    source_header=source_header,
                    structural_header=structural_header,
                    non_empty_cells=non_empty_cells,
                )
            )
        return observations

    @staticmethod
    def _structural_header(table: TableAsset, column_index: int) -> str | None:
        header_paths = table.header_paths or []
        if column_index >= len(header_paths):
            return None
        path = header_paths[column_index]
        if not path:
            return None
        structural_header = normalize_cell(path[-1])
        return structural_header or None

    # ---- evidence builders ------------------------------------------------

    def _lexical_evidence(self, obs: _ColumnObservation) -> list[ColumnSemanticEvidence]:
        if not obs.source_header:
            return [
                ColumnSemanticEvidence(
                    category=EvidenceCategory.LEXICAL,
                    role=None,
                    description="no source header present on this column",
                    weight=0.0,
                )
            ]

        exact = _normalize_header_text(obs.source_header)
        singular = _singularized_header_text(exact)
        exact_roles = _lookup_roles_by_text(exact)
        if exact_roles:
            return [
                ColumnSemanticEvidence(
                    category=EvidenceCategory.LEXICAL,
                    role=role,
                    description=(
                        f"source header {obs.source_header!r} exactly matches "
                        f"role {role.value!r}'s name/alias list"
                    ),
                    weight=self.LEXICAL_EXACT_WEIGHT,
                )
                for role in exact_roles
            ]

        if singular != exact:
            singular_roles = _lookup_roles_by_text(singular)
            if singular_roles:
                return [
                    ColumnSemanticEvidence(
                        category=EvidenceCategory.LEXICAL,
                        role=role,
                        description=(
                            f"source header {obs.source_header!r} matches role "
                            f"{role.value!r} after singularizing to {singular!r}"
                        ),
                        weight=self.LEXICAL_MORPHOLOGICAL_WEIGHT,
                    )
                    for role in singular_roles
                ]

        return [
            ColumnSemanticEvidence(
                category=EvidenceCategory.LEXICAL,
                role=None,
                description=(
                    f"source header {obs.source_header!r} examined; no alias/name match"
                ),
                weight=0.0,
            )
        ]

    def _structural_evidence(self, obs: _ColumnObservation) -> list[ColumnSemanticEvidence]:
        if not obs.structural_header:
            return []
        normalized = _normalize_header_text(obs.structural_header)
        singular = _singularized_header_text(normalized)
        roles = _lookup_roles_by_text(normalized) or (
            _lookup_roles_by_text(singular) if singular != normalized else []
        )
        if not roles:
            return [
                ColumnSemanticEvidence(
                    category=EvidenceCategory.STRUCTURAL,
                    role=None,
                    description=(
                        f"structural label {obs.structural_header!r} examined; "
                        "no alias/name match"
                    ),
                    weight=0.0,
                )
            ]
        return [
            ColumnSemanticEvidence(
                category=EvidenceCategory.STRUCTURAL,
                role=role,
                description=(
                    f"structural label {obs.structural_header!r} (interpreted, "
                    f"not necessarily the literal source header) matches role "
                    f"{role.value!r}"
                ),
                weight=self.STRUCTURAL_WEIGHT,
            )
            for role in roles
        ]

    def _content_evidence(self, obs: _ColumnObservation) -> list[ColumnSemanticEvidence]:
        cells = obs.non_empty_cells
        if not cells:
            return [
                ColumnSemanticEvidence(
                    category=EvidenceCategory.CONTENT,
                    role=None,
                    description="column has no non-empty data cells",
                    weight=0.0,
                )
            ]

        numeric_fraction = sum(_looks_numeric_ish(cell) for cell in cells) / len(cells)
        avg_tokens = sum(len(cell.split()) for cell in cells) / len(cells)

        if numeric_fraction >= self.NUMERIC_FRACTION_THRESHOLD:
            description = (
                f"{numeric_fraction:.0%} of {len(cells)} non-empty cells look numeric-like"
            )
            evidence = [
                ColumnSemanticEvidence(
                    category=EvidenceCategory.CONTENT,
                    role=role,
                    description=description,
                    weight=self.CONTENT_STRONG_WEIGHT,
                )
                for role in _NUMERIC_SUPPORT
            ]
            evidence.extend(
                ColumnSemanticEvidence(
                    category=EvidenceCategory.CONTENT,
                    role=role,
                    description=description + " (opposes free-text roles)",
                    weight=-self.CONTENT_OPPOSE_NUMERIC_WEIGHT,
                )
                for role in _NUMERIC_OPPOSE
            )
            return evidence

        if avg_tokens >= self.RICH_TEXT_AVG_TOKEN_THRESHOLD:
            description = f"average {avg_tokens:.1f} tokens/cell across {len(cells)} cells (rich free text)"
            evidence = [
                ColumnSemanticEvidence(
                    category=EvidenceCategory.CONTENT,
                    role=role,
                    description=description,
                    weight=self.CONTENT_STRONG_WEIGHT,
                )
                for role in _RICH_TEXT_SUPPORT
            ]
            evidence.extend(
                ColumnSemanticEvidence(
                    category=EvidenceCategory.CONTENT,
                    role=role,
                    description=description + " (opposes short-value roles)",
                    weight=-self.CONTENT_OPPOSE_TEXT_WEIGHT,
                )
                for role in _RICH_TEXT_OPPOSE
            )
            return evidence

        if avg_tokens <= self.CODE_LIKE_AVG_TOKEN_THRESHOLD:
            description = (
                f"average {avg_tokens:.1f} tokens/cell across {len(cells)} cells "
                "(short, code-like, non-numeric)"
            )
            return [
                ColumnSemanticEvidence(
                    category=EvidenceCategory.CONTENT,
                    role=role,
                    description=description,
                    weight=self.CONTENT_WEAK_WEIGHT,
                )
                for role in _CODE_LIKE_SUPPORT
            ]

        return [
            ColumnSemanticEvidence(
                category=EvidenceCategory.CONTENT,
                role=None,
                description=(
                    f"average {avg_tokens:.1f} tokens/cell, "
                    f"{numeric_fraction:.0%} numeric-like -- inconclusive content shape"
                ),
                weight=0.0,
            )
        ]

    # ---- scoring passes -----------------------------------------------------

    @staticmethod
    def _scores_from_evidence(
        items: list[ColumnSemanticEvidence],
    ) -> dict[TableColumnSemanticRole, float]:
        scores: dict[TableColumnSemanticRole, float] = {}
        for item in items:
            if item.role is None:
                continue
            scores[item.role] = scores.get(item.role, 0.0) + item.weight
        return scores

    def _relational_pass(
        self,
        raw_scores: dict[int, dict[TableColumnSemanticRole, float]],
    ) -> tuple[dict[int, list[ColumnSemanticEvidence]], dict[int, dict[TableColumnSemanticRole, float]]]:
        max_score_by_role: dict[TableColumnSemanticRole, float] = {}
        owner_by_role: dict[TableColumnSemanticRole, int] = {}
        for column_index, scores in raw_scores.items():
            for role, score in scores.items():
                if score <= 0:
                    continue
                if role not in max_score_by_role or score > max_score_by_role[role]:
                    max_score_by_role[role] = score
                    owner_by_role[role] = column_index

        relational_evidence: dict[int, list[ColumnSemanticEvidence]] = {
            column_index: [] for column_index in raw_scores
        }
        adjusted_scores: dict[int, dict[TableColumnSemanticRole, float]] = {
            column_index: dict(scores) for column_index, scores in raw_scores.items()
        }

        for column_index, scores in raw_scores.items():
            for role, score in scores.items():
                if score <= 0:
                    continue
                max_score = max_score_by_role.get(role, score)
                owner = owner_by_role.get(role)
                is_owner = owner == column_index or (
                    abs(score - max_score) <= self.RELATIONAL_SUPPRESSION_EPSILON
                )
                if is_owner:
                    continue
                adjusted_scores[column_index][role] = score - self.RELATIONAL_SUPPRESSION_WEIGHT
                relational_evidence[column_index].append(
                    ColumnSemanticEvidence(
                        category=EvidenceCategory.RELATIONAL,
                        role=role,
                        description=(
                            f"role {role.value!r} already more strongly supported "
                            f"by column {owner} (score {max_score:.2f} vs {score:.2f})"
                        ),
                        weight=-self.RELATIONAL_SUPPRESSION_WEIGHT,
                    )
                )

        return relational_evidence, adjusted_scores

    def _contextual_pass(
        self,
        table: TableAsset,
        scores: dict[int, dict[TableColumnSemanticRole, float]],
    ) -> tuple[dict[int, list[ColumnSemanticEvidence]], dict[int, dict[TableColumnSemanticRole, float]]]:
        low_trust = (
            table.table_category_confidence is not None
            and table.table_category_confidence < self.CONTEXT_TRUST_THRESHOLD
        ) or (
            table.table_structure_quality is not None
            and table.table_structure_quality < self.CONTEXT_TRUST_THRESHOLD
        )

        context_evidence: dict[int, list[ColumnSemanticEvidence]] = {
            column_index: [] for column_index in scores
        }
        if not low_trust:
            return context_evidence, scores

        description = (
            f"table_category_confidence={table.table_category_confidence!r}, "
            f"table_structure_quality={table.table_structure_quality!r} below "
            f"trust threshold {self.CONTEXT_TRUST_THRESHOLD} -- dampening all "
            "column resolution scores (never raising them)"
        )
        dampened: dict[int, dict[TableColumnSemanticRole, float]] = {}
        for column_index, role_scores in scores.items():
            dampened[column_index] = {
                role: score - self.CONTEXT_DAMPENING_WEIGHT for role, score in role_scores.items()
            }
            if role_scores:
                top_role = max(role_scores, key=lambda role: role_scores[role])
                context_evidence[column_index].append(
                    ColumnSemanticEvidence(
                        category=EvidenceCategory.CONTEXTUAL,
                        role=top_role,
                        description=description,
                        weight=-self.CONTEXT_DAMPENING_WEIGHT,
                    )
                )
        return context_evidence, dampened

    # ---- final decision -----------------------------------------------------

    def _resolve_column(
        self,
        obs: _ColumnObservation,
        evidence: list[ColumnSemanticEvidence],
        scores: dict[TableColumnSemanticRole, float],
    ) -> ColumnSemanticResolution:
        # UNKNOWN means "the classifier cannot establish what this column
        # represents with sufficient confidence" -- this covers zero
        # evidence, weak/below-threshold evidence, and conflicting evidence
        # that never forms a genuinely plausible candidate set. It is
        # deliberately the catch-all below, not merely the "no evidence at
        # all" case.
        #
        # UNMAPPED means something stronger and NOT yet implemented: the
        # classifier would need affirmative, generic evidence that a column
        # represents a *coherent semantic concept* that simply has no slot
        # in the current role vocabulary (e.g. "this is clearly some kind
        # of cross-reference pointer, just not one of our 12 roles") -- as
        # opposed to merely "no role scored highly enough". No evidence
        # source in this classifier currently establishes "coherent but
        # unmapped concept" independently of role-scoring, so UNMAPPED is
        # intentionally unreachable today. The state is kept in the
        # contract for a future evidence source capable of that distinct
        # judgment -- it must not be reached by weak role evidence alone,
        # and no heuristic has been added here merely to make it fire.
        evidence_tuple = tuple(evidence)

        ranked = sorted(
            ((role, score) for role, score in scores.items() if score > 0),
            key=lambda pair: pair[1],
            reverse=True,
        )

        if not ranked:
            return ColumnSemanticResolution(
                column_index=obs.column_index,
                source_header=obs.source_header,
                structural_header=obs.structural_header,
                resolution_state=ColumnResolutionState.UNKNOWN,
                semantic_role=None,
                confidence=None,
                candidate_roles=(),
                evidence=evidence_tuple,
            )

        best_role, best_score = ranked[0]
        second_score = ranked[1][1] if len(ranked) > 1 else 0.0

        if best_score >= self.RESOLVE_FLOOR and (best_score - second_score) >= self.AMBIGUOUS_MARGIN:
            return ColumnSemanticResolution(
                column_index=obs.column_index,
                source_header=obs.source_header,
                structural_header=obs.structural_header,
                resolution_state=ColumnResolutionState.RESOLVED,
                semantic_role=best_role,
                confidence=min(best_score, 1.0),
                candidate_roles=(),
                evidence=evidence_tuple,
            )

        plausible = [
            (role, score) for role, score in ranked if score >= self.PLAUSIBILITY_FLOOR
        ]
        if len(plausible) >= 2 and (best_score - second_score) < self.AMBIGUOUS_MARGIN:
            return ColumnSemanticResolution(
                column_index=obs.column_index,
                source_header=obs.source_header,
                structural_header=obs.structural_header,
                resolution_state=ColumnResolutionState.AMBIGUOUS,
                semantic_role=None,
                confidence=None,
                candidate_roles=tuple(plausible),
                evidence=evidence_tuple,
            )

        # Some role(s) scored above zero but never cleared RESOLVED or
        # AMBIGUOUS -- this is weak/inconclusive evidence, not an
        # affirmatively-understood-but-unmapped concept. UNKNOWN, not
        # UNMAPPED (see module-level note above).
        return ColumnSemanticResolution(
            column_index=obs.column_index,
            source_header=obs.source_header,
            structural_header=obs.structural_header,
            resolution_state=ColumnResolutionState.UNKNOWN,
            semantic_role=None,
            confidence=None,
            candidate_roles=(),
            evidence=evidence_tuple,
        )
