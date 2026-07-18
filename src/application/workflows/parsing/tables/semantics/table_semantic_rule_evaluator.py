from __future__ import annotations

import re

from src.application.workflows.parsing.tables.semantics.table_text_signal_matcher import (
    TableTextSignalMatcher,
)

_EVERY_N_UNIT_PATTERN = re.compile(
    r"\bevery\s+\d+(?:[.,]\d+)?\s*(?:hour|hours|day|days|week|weeks|month|months|year|years|cycle|cycles)\b",
    re.IGNORECASE,
)


class TableSemanticRuleEvaluator:
    def __init__(self, *, signal_matcher: TableTextSignalMatcher | None = None) -> None:
        self.signal_matcher = signal_matcher or TableTextSignalMatcher()

    def looks_like_maintenance_interval_table(
        self,
        headers: list[str],
        labels: list[str],
        direct_text: str,
        section_text: str = "",
    ) -> bool:
        interval_markers = (
            "interval",
            "service interval",
            "maintenance interval",
            "frequency",
            "period",
            "cycle",
            "cycles",
        )
        temporal_markers = (
            "daily",
            "weekly",
            "monthly",
            "quarterly",
            "yearly",
            "annually",
            "annual",
            "semi-annual",
            "semi-annually",
            "bi-annual",
            "biannual",
            "year",
            "years",
            "month",
            "months",
            "hour",
            "hours",
            "every",
            "when needed",
            "regular",
            "regularly",
            "intermittent",
            "periodic",
            "periodically",
        )
        maintenance_markers = (
            "maintenance",
            "inspect",
            "clean",
            "replace",
            "lubric",
            "check",
            "renew",
            "exchange",
            "overhaul",
            "service",
        )
        interval_header_count = self.signal_matcher.count_interval_header_tokens(headers)
        header_text = self.signal_matcher.normalized_text(*headers)
        label_text = self.signal_matcher.normalized_text(*labels)
        interval_hits = self.signal_matcher.count_unique(direct_text, interval_markers)
        temporal_hits = self.signal_matcher.count_unique(direct_text, temporal_markers)
        maintenance_hits = self.signal_matcher.count_unique(
            self.signal_matcher.normalized_text(label_text, direct_text),
            maintenance_markers,
        )
        if interval_header_count >= 2 and maintenance_hits >= 1:
            return True
        # Deliberately checks header_text specifically, NOT direct_text --
        # checking the interval/frequency word anywhere in the body was
        # tried and reverted after a corpus-wide sweep found it stole real
        # troubleshooting/other tables that happen to mention "frequency"
        # in an unrelated sense (e.g. "check that the mains frequency and
        # voltage correspond..."). A header cell actually named
        # "Interval"/"Frequency" is unambiguous; the same word buried in
        # unrelated prose is not. Genuinely collapsed multi-word headers
        # (e.g. "TASK INTERVAL DONE COMMENTS" in one cell) are handled at
        # the source instead, by `has_explicit_header_row` recognizing them
        # as real headers rather than by loosening this check.
        if (
            self.signal_matcher.count_unique(header_text, interval_markers) >= 1
            and maintenance_hits >= 1
            and (interval_hits >= 1 or temporal_hits >= 2)
        ):
            return True
        if (
            len(_EVERY_N_UNIT_PATTERN.findall(direct_text)) >= 2
            and maintenance_hits >= 1
        ):
            return True
        # Real document: a set of fire-safety maintenance-action tables
        # (header "Action | IMO MSC.1-Circ.1432 & MSC.1-Circ.1516 | Marioff
        # recommendations") carries no frequency vocabulary anywhere in its
        # own header or body -- the cadence is expressed entirely by the
        # surrounding document structure, a stack of section headings each
        # named for a distinct testing frequency ("Weekly Testing and
        # Inspections", "Monthly Testing and Inspections", ..., "Five-Year
        # Testing, Inspections and Service"). Requiring 3+ DISTINCT temporal
        # words in the section path (not just 1, which almost any section
        # about scheduled work could incidentally contain) plus real
        # maintenance-verb content in the table itself is a high enough bar
        # that, verified corpus-wide, only this one section family's tables
        # ever reach it.
        # maintenance_hits >= 1 (not >= 2 as elsewhere) is safe here
        # specifically because the section-path gate above is already the
        # narrow, corpus-verified restriction -- it isolates candidates to
        # exactly one section family, so a weaker corroboration requirement
        # doesn't widen exposure to any other document. Several of this
        # family's tables use maintenance verbs only in inflected forms the
        # marker list's whole-word matching doesn't catch as stems
        # ("overhauled", "tested" -- the same class of gap fixed earlier for
        # "year"/"years"), so requiring 2 distinct stem hits would under-fire
        # within this same family for no corpus-wide safety benefit.
        return (
            self.signal_matcher.count_unique(section_text, temporal_markers) >= 3
            and maintenance_hits >= 1
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
            "incident",
            "solution",
            "alarm",
        )
        return (

            self.signal_matcher.count_unique(header_text, troubleshooting_markers) >= 2
        ) or (
            (
                self.signal_matcher.contains(section_text, "trouble shooting")
                or self.signal_matcher.contains(section_text, "troubleshooting")
            )
            and self.signal_matcher.count_unique(direct_text, troubleshooting_markers) >= 2
        )

