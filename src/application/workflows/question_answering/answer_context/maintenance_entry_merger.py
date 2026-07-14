from __future__ import annotations

import re
from collections import OrderedDict
from collections.abc import Sequence
from dataclasses import dataclass

from src.application.workflows.question_answering.answer_context.models import (
    AnswerMaintenanceEntry,
    AnswerMaintenanceReference,
)
from src.application.workflows.question_answering.answer_context.maintenance.maintenance_task_text_cleaner import (
    clean_task,
)
from src.application.workflows.shared.maintenance_action_verbs import (
    MAINTENANCE_ACTION_VERBS,
)
from src.application.workflows.shared.maintenance_text_cleaning import (
    NOT_SPECIFIED,
    clean_interval,
    clean_optional_text,
)

# Bumped whenever the merge-eligibility rules or normalization logic below
# change materially -- mirrors ANSWER_INTENT_RULES_VERSION's convention.
MAINTENANCE_ENTRY_MERGER_RULES_VERSION = "v1"

_WORD_PATTERN = re.compile(r"[a-z0-9]+")
_LEADING_VERB_PATTERN = re.compile(
    r"^(" + "|".join(MAINTENANCE_ACTION_VERBS) + r")\b",
    re.IGNORECASE,
)
_ARTICLES = {"the", "a", "an"}


@dataclass(slots=True)
class _EntryProfile:
    """Caches the four normalized fields _are_mergeable() needs, computed
    once per entry (and once per merge result) instead of being re-derived
    via fresh regex scans on both sides of every pairwise comparison."""

    entry: AnswerMaintenanceEntry
    normalized_interval: str
    leading_action: str
    normalized_task: str
    normalized_component: str


class MaintenanceEntryMerger:
    def merge(
        self,
        entries: Sequence[AnswerMaintenanceEntry],
    ) -> list[AnswerMaintenanceEntry]:
        # We bucket by leading action only, then let _profiles_mergeable()
        # decide whether intervals are compatible. This preserves the old
        # behavior for genuinely different explicit intervals while also
        # allowing a "Not specified" duplicate to merge into the richer
        # interval-bearing record for the same task/component.
        buckets: dict[str, list[dict]] = {}

        for index, entry in enumerate(entries):
            profile = self._build_profile(entry)
            key = profile.leading_action
            bucket = buckets.setdefault(key, [])

            merged = False
            for slot in bucket:
                if self._profiles_mergeable(slot["profile"], profile):
                    merged_entry = self._merge_pair(slot["profile"].entry, entry)
                    slot["profile"] = self._build_profile(merged_entry)
                    merged = True
                    break

            if not merged:
                bucket.append(
                    {
                        "profile": self._build_profile(
                            self._normalized_copy(entry)
                        ),
                        "first_seen_index": index,
                    }
                )

        all_slots = [slot for bucket in buckets.values() for slot in bucket]
        all_slots.sort(key=lambda slot: slot["first_seen_index"])
        return [slot["profile"].entry for slot in all_slots]

    def _build_profile(self, entry: AnswerMaintenanceEntry) -> _EntryProfile:
        return _EntryProfile(
            entry=entry,
            normalized_interval=self._normalize_interval(entry.interval),
            leading_action=self._leading_action(entry.task),
            normalized_task=self._normalize_text(entry.task),
            normalized_component=self._normalize_component(entry.component),
        )

    def _profiles_mergeable(
        self,
        left: _EntryProfile,
        right: _EntryProfile,
    ) -> bool:
        """Task/component half of _are_mergeable(), operating on precomputed
        fields. Leading-action equality is already guaranteed by both
        profiles sharing the same bucket key in merge()."""
        if not self._intervals_compatible(left, right):
            return False
        if left.normalized_task == right.normalized_task:
            return True
        if left.normalized_task in right.normalized_task or right.normalized_task in left.normalized_task:
            return True

        if not left.normalized_component or not right.normalized_component:
            return False
        if left.normalized_component == right.normalized_component:
            return True
        if (
            left.normalized_component in right.normalized_component
            or right.normalized_component in left.normalized_component
        ):
            return True
        return (
            self._token_overlap(left.normalized_component, right.normalized_component)
            >= 0.75
        )

    @staticmethod
    def _intervals_compatible(
        left: _EntryProfile,
        right: _EntryProfile,
    ) -> bool:
        if left.normalized_interval == right.normalized_interval:
            return True
        return (
            left.normalized_interval == "not specified"
            or right.normalized_interval == "not specified"
        )

    def _merge_pair(
        self,
        left: AnswerMaintenanceEntry,
        right: AnswerMaintenanceEntry,
    ) -> AnswerMaintenanceEntry:
        references = self._merge_references(left.references, right.references)
        return AnswerMaintenanceEntry(
            task=self._prefer_task(left.task, right.task),
            description=self._prefer_description(left, right),
            interval=self._merge_interval(left.interval, right.interval),
            component=self._prefer_component(left.component, right.component),
            notes=self._prefer_notes(left.notes, right.notes),
            source_number=references[0].source_number,
            references=references,
        )

    def _normalized_copy(
        self,
        entry: AnswerMaintenanceEntry,
    ) -> AnswerMaintenanceEntry:
        references = self._merge_references(entry.references, [])
        return AnswerMaintenanceEntry(
            task=entry.task,
            description=self._normalized_description(entry),
            interval=self._merge_interval(entry.interval, entry.interval),
            component=self._prefer_component(entry.component, None),
            notes=self._prefer_notes(entry.notes, None),
            source_number=entry.source_number,
            references=references,
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
    def _prefer_task(left: str, right: str) -> str:
        left_clean = clean_task(left) or left
        right_clean = clean_task(right) or right
        return MaintenanceEntryMerger._prefer_more_descriptive_text(
            left_clean,
            right_clean,
        )

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
        if left_clean == NOT_SPECIFIED:
            return right_clean
        if right_clean == NOT_SPECIFIED:
            return left_clean
        if len(right_clean) > len(left_clean):
            return right_clean
        return left_clean

    @staticmethod
    def _clean_interval(value: str | None) -> str:
        return clean_interval(value)

    @staticmethod
    def _clean_optional_text(value: str | None) -> str | None:
        return clean_optional_text(value)

    @staticmethod
    def _leading_action(task: str) -> str:
        normalized_task = clean_task(task) or task
        match = _LEADING_VERB_PATTERN.match(normalized_task.strip())
        if match is None:
            return ""
        return match.group(1).lower()

    @staticmethod
    def _normalize_text(value: str) -> str:
        normalized_value = clean_task(value) or value
        return " ".join(_WORD_PATTERN.findall(normalized_value.lower()))

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
