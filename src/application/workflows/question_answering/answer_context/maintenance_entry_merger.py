from __future__ import annotations

import re
from collections import OrderedDict
from collections.abc import Sequence

from src.application.workflows.question_answering.answer_context.structured_answer_context import (
    AnswerMaintenanceEntry,
    AnswerMaintenanceReference,
)

_WORD_PATTERN = re.compile(r"[a-z0-9]+")
_LEADING_VERB_PATTERN = re.compile(
    r"^(inspect|check|replace|lubricate|clean|test|drain|tighten|calibrate|"
    r"change|grease|service|flush|verify|examine|adjust|renew)\b",
    re.IGNORECASE,
)
_ARTICLES = {"the", "a", "an"}
_NOT_SPECIFIED = "Not specified"


class MaintenanceEntryMerger:
    def merge(
        self,
        entries: Sequence[AnswerMaintenanceEntry],
    ) -> list[AnswerMaintenanceEntry]:
        merged_entries: list[AnswerMaintenanceEntry] = []
        for entry in entries:
            merged = False
            for index, candidate in enumerate(merged_entries):
                if self._are_mergeable(candidate, entry):
                    merged_entries[index] = self._merge_pair(candidate, entry)
                    merged = True
                    break
            if not merged:
                merged_entries.append(self._normalized_copy(entry))
        return merged_entries

    def _are_mergeable(
        self,
        left: AnswerMaintenanceEntry,
        right: AnswerMaintenanceEntry,
    ) -> bool:
        if self._normalize_interval(left.interval) != self._normalize_interval(
            right.interval
        ):
            return False
        left_action = self._leading_action(left.task)
        right_action = self._leading_action(right.task)
        if left_action != right_action:
            return False

        left_task = self._normalize_text(left.task)
        right_task = self._normalize_text(right.task)
        if left_task == right_task:
            return True
        if left_task in right_task or right_task in left_task:
            return True

        left_component = self._normalize_component(left.component)
        right_component = self._normalize_component(right.component)
        if not left_component or not right_component:
            return False
        if left_component == right_component:
            return True
        if left_component in right_component or right_component in left_component:
            return True
        return self._token_overlap(left_component, right_component) >= 0.75

    def _merge_pair(
        self,
        left: AnswerMaintenanceEntry,
        right: AnswerMaintenanceEntry,
    ) -> AnswerMaintenanceEntry:
        references = self._merge_references(left.references, right.references)
        source_numbers = self._merge_ordered_ints(
            left.source_numbers or [left.source_number],
            right.source_numbers or [right.source_number],
        )
        section_paths = self._merge_ordered_strings(
            left.section_paths or ([left.section_path] if left.section_path else []),
            right.section_paths or ([right.section_path] if right.section_path else []),
        )
        return AnswerMaintenanceEntry(
            task=self._prefer_more_descriptive_text(left.task, right.task),
            description=self._prefer_description(left, right),
            interval=self._merge_interval(left.interval, right.interval),
            component=self._prefer_component(left.component, right.component),
            notes=self._prefer_notes(left.notes, right.notes),
            source_number=source_numbers[0],
            source_numbers=source_numbers,
            page_start=self._min_page(left.page_start, right.page_start),
            page_end=self._max_page(left.page_end, right.page_end),
            section_path=section_paths[0] if section_paths else None,
            section_paths=section_paths,
            references=references,
            confidence=max(left.confidence or 0.0, right.confidence or 0.0) or None,
        )

    def _normalized_copy(
        self,
        entry: AnswerMaintenanceEntry,
    ) -> AnswerMaintenanceEntry:
        references = entry.references or [
            AnswerMaintenanceReference(
                source_number=entry.source_number,
                page_start=entry.page_start,
                page_end=entry.page_end,
                section_path=entry.section_path,
            )
        ]
        source_numbers = entry.source_numbers or [entry.source_number]
        section_paths = entry.section_paths or (
            [entry.section_path] if entry.section_path else []
        )
        description = self._normalized_description(entry)
        return AnswerMaintenanceEntry(
            task=entry.task,
            description=description,
            interval=self._merge_interval(entry.interval, entry.interval),
            component=self._prefer_component(entry.component, None),
            notes=self._prefer_notes(entry.notes, None),
            source_number=source_numbers[0],
            source_numbers=source_numbers,
            page_start=entry.page_start,
            page_end=entry.page_end,
            section_path=section_paths[0] if section_paths else None,
            section_paths=section_paths,
            references=self._merge_references(references, []),
            confidence=entry.confidence,
        )

    def _normalized_description(self, entry: AnswerMaintenanceEntry) -> str:
        description_candidates = [
            self._clean_optional_text(entry.description),
            self._clean_optional_text(entry.notes),
            self._clean_optional_text(entry.task),
        ]
        for candidate in description_candidates:
            if candidate is not None:
                return candidate
        return entry.task

    def _prefer_description(
        self,
        left: AnswerMaintenanceEntry,
        right: AnswerMaintenanceEntry,
    ) -> str:
        left_description = self._normalized_description(left)
        right_description = self._normalized_description(right)
        return self._prefer_more_descriptive_text(left_description, right_description)

    def _prefer_notes(self, left: str | None, right: str | None) -> str | None:
        left_cleaned = self._clean_optional_text(left)
        right_cleaned = self._clean_optional_text(right)
        if left_cleaned and right_cleaned:
            return self._prefer_more_descriptive_text(left_cleaned, right_cleaned)
        return left_cleaned or right_cleaned

    def _prefer_component(self, left: str | None, right: str | None) -> str | None:
        left_cleaned = self._clean_optional_text(left)
        right_cleaned = self._clean_optional_text(right)
        if left_cleaned and right_cleaned:
            return self._prefer_more_descriptive_text(left_cleaned, right_cleaned)
        return left_cleaned or right_cleaned

    @staticmethod
    def _prefer_more_descriptive_text(left: str, right: str) -> str:
        left_clean = " ".join(left.split())
        right_clean = " ".join(right.split())
        if len(right_clean) > len(left_clean):
            return right_clean
        return left_clean

    @staticmethod
    def _merge_interval(left: str, right: str) -> str:
        left_clean = MaintenanceEntryMerger._clean_interval(left)
        right_clean = MaintenanceEntryMerger._clean_interval(right)
        if left_clean == _NOT_SPECIFIED:
            return right_clean
        if right_clean == _NOT_SPECIFIED:
            return left_clean
        if len(right_clean) > len(left_clean):
            return right_clean
        return left_clean

    @staticmethod
    def _clean_interval(value: str | None) -> str:
        cleaned = MaintenanceEntryMerger._clean_optional_text(value)
        return cleaned or _NOT_SPECIFIED

    @staticmethod
    def _clean_optional_text(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.strip().split()).rstrip(" .;:")
        if not cleaned:
            return None
        if cleaned.lower() in {"x", "-", "n/a", "na", "unknown"}:
            return None
        return cleaned

    @staticmethod
    def _leading_action(task: str) -> str:
        match = _LEADING_VERB_PATTERN.match(task.strip())
        if match is None:
            return ""
        return match.group(1).lower()

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join(_WORD_PATTERN.findall(value.lower()))

    def _normalize_component(self, value: str | None) -> str:
        cleaned = self._clean_optional_text(value)
        if cleaned is None:
            return ""
        tokens = [token for token in _WORD_PATTERN.findall(cleaned.lower()) if token]
        while tokens and tokens[0] in _ARTICLES:
            tokens.pop(0)
        return " ".join(tokens)

    @staticmethod
    def _normalize_interval(value: str) -> str:
        cleaned = MaintenanceEntryMerger._clean_interval(value)
        return " ".join(_WORD_PATTERN.findall(cleaned.lower()))

    @staticmethod
    def _token_overlap(left: str, right: str) -> float:
        left_tokens = set(left.split())
        right_tokens = set(right.split())
        if not left_tokens or not right_tokens:
            return 0.0
        overlap = len(left_tokens.intersection(right_tokens))
        return overlap / min(len(left_tokens), len(right_tokens))

    def _merge_references(
        self,
        left: Sequence[AnswerMaintenanceReference],
        right: Sequence[AnswerMaintenanceReference],
    ) -> list[AnswerMaintenanceReference]:
        ordered: OrderedDict[
            tuple[int, int | None, int | None, str | None],
            AnswerMaintenanceReference,
        ] = OrderedDict()
        for reference in [*left, *right]:
            key = (
                reference.source_number,
                reference.page_start,
                reference.page_end,
                reference.section_path,
            )
            ordered.setdefault(key, reference)
        return list(ordered.values())

    @staticmethod
    def _merge_ordered_ints(
        left: Sequence[int],
        right: Sequence[int],
    ) -> list[int]:
        ordered: OrderedDict[int, None] = OrderedDict()
        for value in [*left, *right]:
            ordered.setdefault(value, None)
        return list(ordered.keys())

    @staticmethod
    def _merge_ordered_strings(
        left: Sequence[str],
        right: Sequence[str],
    ) -> list[str]:
        ordered: OrderedDict[str, None] = OrderedDict()
        for value in [*left, *right]:
            if value:
                ordered.setdefault(value, None)
        return list(ordered.keys())

    @staticmethod
    def _min_page(left: int | None, right: int | None) -> int | None:
        values = [value for value in (left, right) if value is not None]
        return min(values) if values else None

    @staticmethod
    def _max_page(left: int | None, right: int | None) -> int | None:
        values = [value for value in (left, right) if value is not None]
        return max(values) if values else None
