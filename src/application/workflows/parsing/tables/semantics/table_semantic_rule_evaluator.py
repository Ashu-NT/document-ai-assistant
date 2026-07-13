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

    def looks_like_operation_reference_table(
        self,
        headers: list[str],
        labels: list[str],
        direct_text: str,
        section_text: str,
    ) -> bool:
        header_text = self.signal_matcher.normalized_text(*headers)
        label_text = self.signal_matcher.normalized_text(*labels)
        combined_text = self.signal_matcher.normalized_text(
            header_text,
            label_text,
            direct_text,
            section_text,
        )
        section_markers = (
            "commissioning",
            "configuration",
            "configuring",
            "menu path",
            "operation",
            "operation options",
            "operating",
            "setup",
        )
        ui_markers = (
            "description",
            "dip switch",
            "display",
            "explanation",
            "function",
            "graphic",
            "meaning",
            "operating key",
            "operation",
            "parameter",
            "switch position",
            "symbol",
        )
        action_markers = (
            "accept",
            "activate",
            "confirm",
            "edit mode",
            "enter",
            "exit",
            "navigate",
            "press",
            "reset",
            "save",
            "select",
            "set",
            "switch",
            "unlock",
        )
        section_hits = self.signal_matcher.count_unique(section_text, section_markers)
        header_hits = self.signal_matcher.count_unique(
            self.signal_matcher.normalized_text(header_text, label_text),
            ui_markers,
        )
        direct_hits = self.signal_matcher.count_unique(
            self.signal_matcher.normalized_text(direct_text, label_text),
            ui_markers + action_markers,
        )
        action_hits = self.signal_matcher.count_unique(direct_text, action_markers)
        return (
            section_hits >= 1
            and header_hits >= 1
            and direct_hits >= 2
        ) or (
            header_hits >= 2
            and action_hits >= 1
            and self.signal_matcher.count_unique(combined_text, section_markers) >= 1
        )

    def looks_like_operating_limits_table(
        self,
        headers: list[str],
        labels: list[str],
        direct_text: str,
    ) -> bool:
        header_text = self.signal_matcher.normalized_text(*headers)
        label_text = self.signal_matcher.normalized_text(*labels)
        direct_markers = (
            "ambient temperature",
            "current",
            "intrinsically safe",
            "operating limit",
            "power supply",
            "pressure",
            "process temperature",
            "protection",
            "range",
            "supply voltage",
            "temperature",
            "temperature class",
            "voltage",
        )
        header_markers = (
            "current",
            "limit",
            "power supply",
            "pressure",
            "protection",
            "range",
            "supply voltage",
            "temperature",
            "voltage",
        )
        return self.signal_matcher.count_unique(direct_text, direct_markers) >= 2 and any(
            self.signal_matcher.contains(header_text, marker)
            or self.signal_matcher.contains(label_text, marker)
            for marker in header_markers
        )

    def looks_like_technical_data_table(
        self,
        headers: list[str],
        labels: list[str],
        direct_text: str,
        section_text: str,
    ) -> bool:
        header_text = self.signal_matcher.normalized_text(*headers)
        label_text = self.signal_matcher.normalized_text(*labels)
        technical_markers = (
            "capacity",
            "calibration",
            "current",
            "deviation",
            "dimension",
            "flow rate",
            "installed power",
            "material",
            "measurement error",
            "output",
            "output signal",
            "parameter",
            "power",
            "pressure",
            "pump type",
            "reference pressure",
            "rpm",
            "serial number",
            "specification",
            "temperature",
            "test point",
            "value",
            "voltage",
            "weight",
            "year of manufacture",
        )
        direct_hits = self.signal_matcher.count_unique(direct_text, technical_markers)
        label_hits = self.signal_matcher.count_unique(label_text, technical_markers)
        has_explicit_header = any(
            header in {"parameter", "value", "description", "specification"}
            for header in headers
        )
        return direct_hits >= 2 and (
            has_explicit_header
            or label_hits >= 2
            or self.signal_matcher.contains(header_text, "technical data")
            or self.signal_matcher.contains(section_text, "technical data")
            or (
                self.signal_matcher.count_unique(
                    direct_text,
                    ("oil", "quantity", "specification", "viscosity", "grade"),
                ) >= 2
                and self.signal_matcher.count_unique(
                    self.signal_matcher.normalized_text(header_text, label_text),
                    ("oil", "quantity", "specification"),
                ) >= 1
            )
        )

    def looks_like_certification_table(
        self,
        direct_text: str,
        section_text: str,
    ) -> bool:
        direct_markers = (
            "approval",
            "atex",
            "certificate",
            "class",
            "conformity",
            "iecex",
            "particulars",
        )
        section_markers = ("certificate", "approval", "certification")
        return self.signal_matcher.count_unique(direct_text, direct_markers) >= 2 or (
            any(
                self.signal_matcher.contains(section_text, marker)
                for marker in section_markers
            )
            and self.signal_matcher.count_unique(
                direct_text,
                ("approval", "atex", "class", "conformity", "iecex", "particulars"),
            ) >= 1
        )

    def body_label_cells(
        self,
        rows: list[list[str]],
        *,
        has_header_row: bool,
    ) -> list[str]:
        labels: list[str] = []
        for row in rows:
            non_empty = [str(cell or "").strip().casefold() for cell in row if str(cell or "").strip()]
            if len(non_empty) >= 2:
                labels.append(non_empty[0])
            elif not has_header_row and non_empty:
                labels.append(non_empty[0])
        return labels

    def body_text(self, rows: list[list[str]]) -> str:
        return self.signal_matcher.normalized_text(
            *[
                str(cell or "").strip()
                for row in rows
                for cell in row
                if str(cell or "").strip()
            ]
        )
