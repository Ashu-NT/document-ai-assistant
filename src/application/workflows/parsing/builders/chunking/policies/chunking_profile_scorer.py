from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_inference import (
    ChunkingProfileInference,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_statistics import (
    ChunkingProfileStatistics,
)


class ChunkingProfileScorer:
    def score(
        self,
        statistics: ChunkingProfileStatistics,
    ) -> ChunkingProfileInference:
        scores = {
            profile: 0.0
            for profile in ChunkingProfile
        }
        reasons = {
            profile: []
            for profile in ChunkingProfile
        }

        self._score_manual(scores, reasons, statistics)
        self._score_datasheet(scores, reasons, statistics)
        self._score_drawing(scores, reasons, statistics)
        self._score_report(scores, reasons, statistics)
        self._score_default(scores, reasons, statistics)

        rounded_scores = {
            profile: round(max(0.0, score), 3)
            for profile, score in scores.items()
        }
        selected_profile = self._select_profile(rounded_scores)
        confidence = self._confidence(
            selected_profile=selected_profile,
            scores=rounded_scores,
        )
        return ChunkingProfileInference(
            selected_profile=selected_profile,
            confidence=confidence,
            scores=rounded_scores,
            reasons=reasons,
            statistics=statistics,
        )

    @staticmethod
    def _score_manual(
        scores: dict[ChunkingProfile, float],
        reasons: dict[ChunkingProfile, list[str]],
        statistics: ChunkingProfileStatistics,
    ) -> None:
        if statistics.manual_marker_hits > 0:
            scores[ChunkingProfile.MANUAL] += min(
                5.0,
                statistics.manual_marker_hits * 1.6,
            )
            reasons[ChunkingProfile.MANUAL].append(
                f"Manual markers found in title/sections ({statistics.manual_marker_hits} hits)."
            )

        if statistics.procedure_like_section_count > 0:
            scores[ChunkingProfile.MANUAL] += min(
                2.0,
                0.8 + (statistics.procedure_like_section_count * 0.4),
            )
            reasons[ChunkingProfile.MANUAL].append(
                f"Procedure-like section titles are present ({statistics.procedure_like_section_count})."
            )

        if statistics.list_ratio >= 0.12:
            scores[ChunkingProfile.MANUAL] += 1.3
            reasons[ChunkingProfile.MANUAL].append(
                f"List items are common (ratio {statistics.list_ratio:.2f})."
            )

        if (
            statistics.long_text_ratio >= 0.25
            and (
                statistics.manual_marker_hits > 0
                or statistics.procedure_like_section_count > 0
            )
        ):
            scores[ChunkingProfile.MANUAL] += 1.2
            reasons[ChunkingProfile.MANUAL].append(
                f"Narrative text blocks are present (long-text ratio {statistics.long_text_ratio:.2f})."
            )

        if statistics.max_section_depth >= 3 or statistics.nested_section_ratio >= 0.35:
            scores[ChunkingProfile.MANUAL] += 0.8
            reasons[ChunkingProfile.MANUAL].append(
                f"Section hierarchy is task-oriented or nested (depth {statistics.max_section_depth})."
            )

    @staticmethod
    def _score_datasheet(
        scores: dict[ChunkingProfile, float],
        reasons: dict[ChunkingProfile, list[str]],
        statistics: ChunkingProfileStatistics,
    ) -> None:
        if statistics.datasheet_marker_hits > 0:
            scores[ChunkingProfile.DATASHEET] += min(
                5.0,
                statistics.datasheet_marker_hits * 1.7,
            )
            reasons[ChunkingProfile.DATASHEET].append(
                f"Datasheet/specification markers found in title/sections ({statistics.datasheet_marker_hits} hits)."
            )

        if statistics.table_ratio >= 0.22:
            scores[ChunkingProfile.DATASHEET] += 2.5
            reasons[ChunkingProfile.DATASHEET].append(
                f"Tables are dominant (ratio {statistics.table_ratio:.2f})."
            )
        elif statistics.table_ratio >= 0.12:
            scores[ChunkingProfile.DATASHEET] += 1.2
            reasons[ChunkingProfile.DATASHEET].append(
                f"Tables are a notable structural signal (ratio {statistics.table_ratio:.2f})."
            )

        if statistics.short_text_ratio >= 0.35:
            scores[ChunkingProfile.DATASHEET] += 1.2
            reasons[ChunkingProfile.DATASHEET].append(
                f"Text blocks are short and spec-like (short-text ratio {statistics.short_text_ratio:.2f})."
            )

        if 0 < statistics.avg_text_tokens <= 14:
            scores[ChunkingProfile.DATASHEET] += 0.9
            reasons[ChunkingProfile.DATASHEET].append(
                f"Average text blocks are concise ({statistics.avg_text_tokens:.1f} tokens)."
            )

        if statistics.max_section_depth <= 2 and statistics.root_section_count >= statistics.nested_section_count:
            scores[ChunkingProfile.DATASHEET] += 0.6
            reasons[ChunkingProfile.DATASHEET].append(
                "Section structure is shallow, which fits specification-style documents."
            )

        if statistics.manual_marker_hits >= 3 or statistics.procedure_like_section_count >= 2:
            scores[ChunkingProfile.DATASHEET] -= 2.0
            reasons[ChunkingProfile.DATASHEET].append(
                "Strong manual/procedure signals reduce datasheet confidence."
            )

        if statistics.long_text_ratio >= 0.35:
            scores[ChunkingProfile.DATASHEET] -= 1.0
            reasons[ChunkingProfile.DATASHEET].append(
                "Long narrative text is less typical for a datasheet."
            )

    @staticmethod
    def _score_drawing(
        scores: dict[ChunkingProfile, float],
        reasons: dict[ChunkingProfile, list[str]],
        statistics: ChunkingProfileStatistics,
    ) -> None:
        if statistics.drawing_marker_hits > 0:
            scores[ChunkingProfile.DRAWING] += min(
                5.0,
                statistics.drawing_marker_hits * 1.7,
            )
            reasons[ChunkingProfile.DRAWING].append(
                f"Drawing/schematic markers found in title/sections ({statistics.drawing_marker_hits} hits)."
            )

        if statistics.picture_ratio >= 0.22:
            scores[ChunkingProfile.DRAWING] += 2.6
            reasons[ChunkingProfile.DRAWING].append(
                f"Pictures are dominant (ratio {statistics.picture_ratio:.2f})."
            )
        elif statistics.picture_ratio >= 0.12:
            scores[ChunkingProfile.DRAWING] += 1.1
            reasons[ChunkingProfile.DRAWING].append(
                f"Pictures are a meaningful structural signal (ratio {statistics.picture_ratio:.2f})."
            )

        if statistics.caption_ratio >= 0.08:
            scores[ChunkingProfile.DRAWING] += 0.7
            reasons[ChunkingProfile.DRAWING].append(
                f"Caption density supports figure-driven content (ratio {statistics.caption_ratio:.2f})."
            )

        if statistics.text_element_count == 0 or statistics.avg_text_tokens <= 8:
            scores[ChunkingProfile.DRAWING] += 1.4
            reasons[ChunkingProfile.DRAWING].append(
                "Text density is very low, which fits drawing-like documents."
            )

        if statistics.long_text_ratio <= 0.10 and statistics.text_element_count > 0:
            scores[ChunkingProfile.DRAWING] += 1.0
            reasons[ChunkingProfile.DRAWING].append(
                f"Long narrative text is rare (long-text ratio {statistics.long_text_ratio:.2f})."
            )

        if statistics.avg_text_tokens >= 16 or statistics.long_text_ratio >= 0.25:
            scores[ChunkingProfile.DRAWING] -= 2.4
            reasons[ChunkingProfile.DRAWING].append(
                "Text-rich structure reduces drawing confidence."
            )

        if statistics.list_ratio >= 0.12:
            scores[ChunkingProfile.DRAWING] -= 1.2
            reasons[ChunkingProfile.DRAWING].append(
                "Frequent list items are atypical for drawing-centric documents."
            )

    @staticmethod
    def _score_report(
        scores: dict[ChunkingProfile, float],
        reasons: dict[ChunkingProfile, list[str]],
        statistics: ChunkingProfileStatistics,
    ) -> None:
        if statistics.report_marker_hits > 0:
            scores[ChunkingProfile.REPORT] += min(
                5.0,
                statistics.report_marker_hits * 1.7,
            )
            reasons[ChunkingProfile.REPORT].append(
                f"Report markers found in title/sections ({statistics.report_marker_hits} hits)."
            )

        if statistics.long_text_ratio >= 0.35:
            scores[ChunkingProfile.REPORT] += 1.8
            reasons[ChunkingProfile.REPORT].append(
                f"Narrative text blocks are common (long-text ratio {statistics.long_text_ratio:.2f})."
            )

        if statistics.avg_text_tokens >= 18:
            scores[ChunkingProfile.REPORT] += 1.1
            reasons[ChunkingProfile.REPORT].append(
                f"Average text blocks are long ({statistics.avg_text_tokens:.1f} tokens)."
            )

        if statistics.section_count >= 4:
            scores[ChunkingProfile.REPORT] += 0.7
            reasons[ChunkingProfile.REPORT].append(
                f"Document has multiple narrative sections ({statistics.section_count})."
            )

        if statistics.nested_section_ratio >= 0.20:
            scores[ChunkingProfile.REPORT] += 0.6
            reasons[ChunkingProfile.REPORT].append(
                f"Section hierarchy supports report-style structure (nested ratio {statistics.nested_section_ratio:.2f})."
            )

        if statistics.manual_marker_hits >= 3 and statistics.procedure_like_section_count >= 2:
            scores[ChunkingProfile.REPORT] -= 1.4
            reasons[ChunkingProfile.REPORT].append(
                "Strong procedure/task structure reduces report confidence."
            )

    @staticmethod
    def _score_default(
        scores: dict[ChunkingProfile, float],
        reasons: dict[ChunkingProfile, list[str]],
        statistics: ChunkingProfileStatistics,
    ) -> None:
        non_default_scores = sorted(
            (
                score
                for profile, score in scores.items()
                if profile != ChunkingProfile.DEFAULT
            ),
            reverse=True,
        )
        top_score = non_default_scores[0] if non_default_scores else 0.0
        second_score = non_default_scores[1] if len(non_default_scores) > 1 else 0.0
        gap = top_score - second_score

        if top_score < 3.0:
            scores[ChunkingProfile.DEFAULT] += 3.0
            reasons[ChunkingProfile.DEFAULT].append(
                "Structural signals are weak across all profile candidates."
            )
        elif top_score < 4.5:
            scores[ChunkingProfile.DEFAULT] += 1.3
            reasons[ChunkingProfile.DEFAULT].append(
                "No structural profile is strongly dominant."
            )

        if gap < 0.75:
            scores[ChunkingProfile.DEFAULT] += 2.5
            reasons[ChunkingProfile.DEFAULT].append(
                "Top structural profile scores are too close, so the document is ambiguous."
            )
        elif gap < 1.5:
            scores[ChunkingProfile.DEFAULT] += 0.9
            reasons[ChunkingProfile.DEFAULT].append(
                "Top structural profile scores are relatively close."
            )

        if statistics.total_marker_hits == 0:
            scores[ChunkingProfile.DEFAULT] += 0.8
            reasons[ChunkingProfile.DEFAULT].append(
                "No strong profile markers were found in the title or section headings."
            )

        if statistics.element_count < 4:
            scores[ChunkingProfile.DEFAULT] += 0.6
            reasons[ChunkingProfile.DEFAULT].append(
                "Very small documents do not provide enough structural evidence."
            )

    @staticmethod
    def _select_profile(
        scores: dict[ChunkingProfile, float],
    ) -> ChunkingProfile:
        ordered = sorted(
            scores.items(),
            key=lambda item: (
                item[1],
                item[0] == ChunkingProfile.DEFAULT,
            ),
            reverse=True,
        )
        return ordered[0][0]

    @staticmethod
    def _confidence(
        *,
        selected_profile: ChunkingProfile,
        scores: dict[ChunkingProfile, float],
    ) -> float:
        ordered_scores = sorted(scores.values(), reverse=True)
        top_score = ordered_scores[0] if ordered_scores else 0.0
        second_score = ordered_scores[1] if len(ordered_scores) > 1 else 0.0
        normalized_top = min(1.0, top_score / 8.0)
        gap_ratio = min(1.0, (top_score - second_score) / max(top_score, 1.0))
        confidence = 0.15 + (0.45 * normalized_top) + (0.40 * gap_ratio)

        if selected_profile == ChunkingProfile.DEFAULT:
            confidence = min(confidence, 0.6)

        return round(min(0.99, max(0.0, confidence)), 3)
