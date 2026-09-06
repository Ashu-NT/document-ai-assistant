from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates.heading_candidate_assessment import (
    HeadingCandidateAssessment,
)
from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates.heading_candidate_role import (
    HeadingCandidateRole,
)
from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates.heading_candidate_signals import (
    HeadingCandidateSignals,
)


class HeadingCandidateScorer:
    """Combines independent structural signals without granting one authority."""

    _DEMOTION_THRESHOLD = 7.0
    _DEMOTION_MARGIN = 2.0

    def assess(self, signals: HeadingCandidateSignals) -> HeadingCandidateAssessment:
        scores = {role: 0.0 for role in HeadingCandidateRole}
        reasons: list[str] = []
        self._score_outline(signals, scores, reasons)
        self._score_table_category(signals, scores, reasons)
        self._score_local_label(signals, scores, reasons)
        self._score_caption_and_noise(signals, scores, reasons)

        role = self._select_role(scores, signals)
        competing_score = max(
            score for candidate, score in scores.items() if candidate != role
        )
        margin = scores[role] - competing_score
        confidence = min(0.99, max(0.5, 0.58 + max(0.0, margin) / 20.0))
        return HeadingCandidateAssessment(
            role=role,
            confidence=round(confidence, 4),
            scores={candidate: round(score, 3) for candidate, score in scores.items()},
            reasons=tuple(reasons),
        )

    @staticmethod
    def _score_outline(signals, scores, reasons) -> None:
        score = 0.0
        if signals.toc_matched:
            score += 3.0
            reasons.append("toc_match")
        if signals.toc_title_exact:
            score += 3.0
            reasons.append("toc_title_exact")
        if signals.toc_number_exact:
            score += 2.0
            reasons.append("toc_number_exact")
        if signals.toc_page_close:
            score += 1.0
            reasons.append("toc_page_close")
        if signals.numbering_compatible is True:
            score += 4.0
            reasons.append("numbering_compatible")
        if signals.has_descendant_pattern:
            score += 4.0
            reasons.append("numbered_descendant_pattern")
        if signals.has_sibling_pattern:
            score += 3.0
            reasons.append("numbered_sibling_pattern")
        if signals.native_heading_level is not None:
            score += 2.0
            reasons.append("native_heading_level")
        if signals.layout_prominent:
            score += 1.0
            reasons.append("layout_prominence")
        if signals.page_continuous:
            score += 0.5
        if signals.implausible_hierarchy_jump:
            score -= 4.0
            reasons.append("implausible_hierarchy_jump")
        if signals.adjacent_table and signals.numbering_compatible is False:
            score -= 2.0
        scores[HeadingCandidateRole.OUTLINE_SECTION] = score

    @staticmethod
    def _score_table_category(signals, scores, reasons) -> None:
        score = 0.0
        if signals.adjacent_table:
            score += 5.0
            reasons.append("adjacent_table")
        if signals.active_scope_depth is not None:
            score += 1.5
        if signals.numbering_compatible is False:
            score += 3.0
            reasons.append("numbering_conflicts_with_active_scope")
        if signals.title_word_count <= 6:
            score += 1.0
        if not signals.has_descendant_pattern:
            score += 1.0
        if signals.indented_from_active:
            score += 1.0
            reasons.append("layout_indented_from_scope")
        scores[HeadingCandidateRole.TABLE_CATEGORY] = score

    @staticmethod
    def _score_local_label(signals, scores, reasons) -> None:
        score = 0.0
        if signals.repeated_title_count >= 2:
            score += 3.0
            reasons.append("repeated_local_title")
        if signals.embedded_item_numbering and signals.active_scope_depth is not None:
            score += 5.0
            reasons.append("embedded_item_numbering")
        if signals.ends_with_colon:
            score += 2.0
            reasons.append("label_punctuation")
        if signals.active_scope_depth is not None:
            score += 1.0
        if signals.numbering_compatible is False:
            score += 2.0
        if signals.indented_from_active:
            score += 1.0
        scores[HeadingCandidateRole.LOCAL_LABEL] = score

    @staticmethod
    def _score_caption_and_noise(signals, scores, reasons) -> None:
        if signals.caption_like:
            scores[HeadingCandidateRole.CAPTION] += 6.0
            reasons.append("caption_text_pattern")
        if signals.caption_like and (
            signals.adjacent_picture or signals.adjacent_table
        ):
            scores[HeadingCandidateRole.CAPTION] += 2.0
        if signals.noise_like:
            scores[HeadingCandidateRole.NOISE] += 10.0
            reasons.append("non_content_or_furniture")

    def _select_role(
        self,
        scores: dict[HeadingCandidateRole, float],
        signals: HeadingCandidateSignals,
    ) -> HeadingCandidateRole:
        if signals.noise_like:
            return HeadingCandidateRole.NOISE
        if signals.caption_like and scores[HeadingCandidateRole.CAPTION] >= 6.0:
            return HeadingCandidateRole.CAPTION

        outline_score = scores[HeadingCandidateRole.OUTLINE_SECTION]
        alternatives = (
            HeadingCandidateRole.TABLE_CATEGORY,
            HeadingCandidateRole.LOCAL_LABEL,
        )
        best_alternative = max(alternatives, key=scores.__getitem__)
        if (
            best_alternative == HeadingCandidateRole.TABLE_CATEGORY
            and signals.numbering_compatible is not False
            and not signals.implausible_hierarchy_jump
            and not signals.indented_from_active
            and signals.repeated_title_count < 2
        ):
            return HeadingCandidateRole.OUTLINE_SECTION
        if (
            best_alternative == HeadingCandidateRole.LOCAL_LABEL
            and signals.repeated_title_count < 2
            and not (signals.ends_with_colon and signals.indented_from_active)
            and not signals.embedded_item_numbering
        ):
            return HeadingCandidateRole.OUTLINE_SECTION
        if (
            scores[best_alternative] >= self._DEMOTION_THRESHOLD
            and scores[best_alternative] >= outline_score + self._DEMOTION_MARGIN
        ):
            return best_alternative
        return HeadingCandidateRole.OUTLINE_SECTION
