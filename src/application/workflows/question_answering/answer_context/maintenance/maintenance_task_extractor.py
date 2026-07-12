from __future__ import annotations

import re
from typing import Sequence

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.maintenance.maintenance_candidate_parser import (
    MaintenanceCandidate,
    candidate_from_line,
    candidate_from_table_row,
    parse_table_cells,
    parse_table_header,
)
from src.application.workflows.question_answering.answer_context.maintenance.maintenance_table_candidate_extractor import (
    MaintenanceTableCandidateExtractor,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerMaintenanceEntry,
    AnswerMaintenanceReference,
    AnswerSource,
)
from src.application.workflows.question_answering.answer_context.tables import (
    AnswerTable,
    AnswerTableProjector,
)

_HEADER_SEPARATOR_PATTERN = re.compile(
    r"^\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)+\|?$"
)


class MaintenanceTaskExtractor:
    def __init__(
        self,
        maintenance_table_candidate_extractor: MaintenanceTableCandidateExtractor | None = None,
        answer_table_projector: AnswerTableProjector | None = None,
    ) -> None:
        self.maintenance_table_candidate_extractor = (
            maintenance_table_candidate_extractor or MaintenanceTableCandidateExtractor()
        )
        self.answer_table_projector = answer_table_projector or AnswerTableProjector()

    def extract_maintenance_entries(
        self,
        sources: Sequence[AnswerSource],
        *,
        answer_intent: AnswerIntent,
        tables: Sequence[AnswerTable] | None = None,
    ) -> list[AnswerMaintenanceEntry]:
        if answer_intent != AnswerIntent.MAINTENANCE_SUMMARY:
            return []

        entries: list[AnswerMaintenanceEntry] = []
        seen: set[tuple[int, str, str, str]] = set()
        resolved_tables = list(tables) if tables is not None else self.answer_table_projector.build(sources)
        tables_by_source_number = {
            table.source_number: table for table in resolved_tables
        }
        for source in sources:
            candidates = list(
                self._source_candidates(
                    source,
                    table=tables_by_source_number.get(source.source_number),
                )
            )
            for candidate in candidates:
                fingerprint = (
                    source.source_number,
                    candidate.task.lower(),
                    candidate.interval.lower(),
                    (candidate.component or "").lower(),
                )
                if fingerprint in seen:
                    continue
                seen.add(fingerprint)
                entries.append(
                    AnswerMaintenanceEntry(
                        task=candidate.task,
                        description=candidate.description,
                        interval=candidate.interval,
                        component=candidate.component,
                        notes=candidate.notes,
                        source_number=source.source_number,
                        references=[
                            AnswerMaintenanceReference(
                                source_number=source.source_number,
                                page_start=source.page_start,
                                page_end=source.page_end,
                                section_path=source.section_path,
                            )
                        ],
                    )
                )
        return entries

    def _source_candidates(
        self,
        source: AnswerSource,
        *,
        table: AnswerTable | None,
    ):
        if table is not None:
            table_candidates = self.maintenance_table_candidate_extractor.extract(table)
            if table_candidates:
                yield from table_candidates
                return

        yield from self._maintenance_candidates(source.content)
        if source.table_rows:
            yield from self._maintenance_candidates_from_rows(source.table_rows)

    def _maintenance_candidates(
        self,
        content: str,
    ) -> list[MaintenanceCandidate]:
        candidates: list[MaintenanceCandidate] = []
        table_header: list[str] | None = None
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                table_header = None
                continue
            if _HEADER_SEPARATOR_PATTERN.match(stripped):
                continue
            if "|" in stripped:
                cells = parse_table_cells(stripped)
                if len(cells) >= 2:
                    header = parse_table_header(cells)
                    if header is not None:
                        table_header = header
                        continue
                    table_candidate = candidate_from_table_row(
                        cells,
                        table_header=table_header,
                    )
                    if table_candidate is not None:
                        candidates.append(table_candidate)
                        continue

            line_candidate = candidate_from_line(stripped)
            if line_candidate is not None:
                candidates.append(line_candidate)
        return candidates

    def _maintenance_candidates_from_rows(
        self,
        rows: list[list[str]],
    ) -> list[MaintenanceCandidate]:
        if not rows:
            return []

        table_header = parse_table_header(rows[0])
        body_rows = rows[1:] if table_header is not None else rows
        candidates: list[MaintenanceCandidate] = []
        for cells in body_rows:
            if len(cells) < 2:
                continue
            table_candidate = candidate_from_table_row(
                cells,
                table_header=table_header,
            )
            if table_candidate is not None:
                candidates.append(table_candidate)
        return candidates
