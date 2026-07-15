from __future__ import annotations

from src.application.workflows.parsing.tables.semantics.table_text_signal_matcher import (
    TableTextSignalMatcher,
)


class TableSemanticRuleEvaluator:
    def __init__(self, *, signal_matcher: TableTextSignalMatcher | None = None) -> None:
        self.signal_matcher = signal_matcher or TableTextSignalMatcher()

    def looks_like_maintenance_interval_table(
        self,
        headers: list[str],
        labels: list[str],
        direct_text: str,
    ) -> bool:
        interval_markers = (
            "interval",
            "service interval",
            "maintenance interval",
            "frequency",
            "period",
        )
        temporal_markers = (
            "daily",
            "weekly",
            "monthly",
            "quarterly",
            "yearly",
            "year",
            "month",
            "months",
            "hour",
            "hours",
            "every",
            "when needed",
        )
        maintenance_markers = ("maintenance", "inspect", "clean", "replace", "lubric", "check")
        interval_header_count = self.signal_matcher.count_interval_header_tokens(headers)
        header_text = self.signal_matcher.normalized_text(*headers)
        label_text = self.signal_matcher.normalized_text(*labels)
        interval_hits = self.signal_matcher.count_unique(direct_text, interval_markers)
        temporal_hits = self.signal_matcher.count_unique(direct_text, temporal_markers)
        maintenance_hits = self.signal_matcher.count_unique(
            self.signal_matcher.normalized_text(label_text, direct_text),
            maintenance_markers,
        )
        return (
            interval_header_count >= 2 and maintenance_hits >= 1
        ) or (
            self.signal_matcher.count_unique(header_text, interval_markers) >= 1
            and maintenance_hits >= 1
            and (interval_hits >= 1 or temporal_hits >= 2)
        )

    def looks_like_lubrication_schedule_table(
        self,
        headers: list[str],
        labels: list[str],
        direct_text: str,
        section_text: str,
    ) -> bool:
        header_text = self.signal_matcher.normalized_text(*headers)
        label_text = self.signal_matcher.normalized_text(*labels)
        maintenance_markers = (
            "lubrication",
            "grease",
            "oil",
            "service interval",
            "maintenance interval",
            "schedule",
        )
        temporal_markers = (
            "daily",
            "weekly",
            "monthly",
            "quarterly",
            "yearly",
            "hour",
            "hours",
            "when needed",
        )
        maintenance_hits = self.signal_matcher.count_unique(
            self.signal_matcher.normalized_text(
                header_text,
                label_text,
                direct_text,
                section_text,
            ),
            maintenance_markers,
        )
        temporal_hits = self.signal_matcher.count_unique(
            self.signal_matcher.normalized_text(header_text, label_text, direct_text),
            temporal_markers,
        )
        return (
            self.signal_matcher.contains(section_text, "lubrication schedule")
            and maintenance_hits >= 2
            and temporal_hits >= 1
        )

    def looks_like_troubleshooting_table(
        self,
        headers: list[str],
        direct_text: str,
        section_text: str,
    ) -> bool:
        header_text = self.signal_matcher.normalized_text(*headers)
        troubleshooting_markers = (
            "fault",
            "problem",
            "symptom",
            "cause",
            "causes",
            "remedy",
            "remedies",
            "corrective action",
        )
        return (
            self.signal_matcher.count_unique(direct_text, troubleshooting_markers) >= 3
            and self.signal_matcher.count_unique(header_text, troubleshooting_markers) >= 2
        ) or (
            (
                self.signal_matcher.contains(section_text, "trouble shooting")
                or self.signal_matcher.contains(section_text, "troubleshooting")
            )
            and self.signal_matcher.count_unique(direct_text, troubleshooting_markers) >= 2
        )

