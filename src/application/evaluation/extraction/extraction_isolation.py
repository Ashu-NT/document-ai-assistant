"""Isolation seams for running the REAL production `ExtractionWorkflow`
without contaminating production state - mirrors the `_SuppliedArtifactParser`
/ `workflow.parsed_artifact_store = None` pattern already used for the MTU
CHALLENGE parsing evaluation (see test_mtu_challenge_structural_regression.py),
applied to the extraction workflow's two external seams: the LLM port and
the repository/UnitOfWork.

`ExtractionWorkflow.extract()` unconditionally calls
`extraction_service.save_extraction_result()`/`.replace_extraction_result()`
at the end (no "skip persistence" branch exists) - so isolation here means
injecting a REAL `ExtractionService` backed by an in-memory
`ExtractionRepository` implementation, never bypassing
`ExtractionResultValidator`, exactly as the Phase 2B research recommended.
"""

from dataclasses import dataclass, field
from typing import Any

from src.application.contracts.extraction import ExtractionRepository
from src.domain.extraction import (
    ContactPoint,
    EquipmentInfo,
    ExtractionResult,
    MaintenanceInterval,
    MaintenanceTask,
    Manufacturer,
    Procedure,
    SafetyWarning,
    SemanticRelationship,
    SparePart,
    Specification,
    Supplier,
    TroubleshootingEntry,
)


@dataclass(slots=True)
class RecordedLLMCall:
    prompt: str
    model: str | None
    temperature: float | None
    json_mode: bool
    response_schema: dict[str, Any] | None
    num_ctx: int | None


class CannedResponseLLMService:
    """Duck-types `LLMService.generate(...)` with a queue of pre-written
    JSON response strings, popped in call order. Raises loudly (rather
    than looping/blocking) if the queue runs out, since a batch count
    mismatch between the fixture author and the real chunk batcher is a
    real bug to surface, not silently paper over.

    Also supports `real_llm_service`-delegation mode: if constructed with
    `delegate=<a real LLMService>` instead of `responses`, every call is
    forwarded to the real provider (used for the "fresh model" real-run
    mode) while still recording every call for reproducibility reporting.
    """

    def __init__(
        self,
        responses: list[str] | None = None,
        *,
        delegate: Any | None = None,
    ) -> None:
        if responses is not None and delegate is not None:
            raise ValueError("Pass either `responses` or `delegate`, not both.")
        self.responses = list(responses) if responses is not None else None
        self.delegate = delegate
        self.calls: list[RecordedLLMCall] = []

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
        response_schema: dict[str, Any] | None = None,
        num_ctx: int | None = None,
    ) -> str:
        self.calls.append(
            RecordedLLMCall(
                prompt=prompt,
                model=model,
                temperature=temperature,
                json_mode=json_mode,
                response_schema=response_schema,
                num_ctx=num_ctx,
            )
        )
        if self.delegate is not None:
            return self.delegate.generate(
                prompt,
                model=model,
                temperature=temperature,
                json_mode=json_mode,
                response_schema=response_schema,
                num_ctx=num_ctx,
            )
        assert self.responses is not None
        if not self.responses:
            raise RuntimeError(
                "CannedResponseLLMService ran out of canned responses - "
                f"{len(self.calls)} call(s) made. This means the real chunk "
                "batcher produced more batches than the fixture anticipated; "
                "investigate rather than looping the last response."
            )
        return self.responses.pop(0)


@dataclass(slots=True)
class InMemoryExtractionRepository:
    """Full `ExtractionRepository` Protocol implementation backed by plain
    dicts - never touches a real database/UnitOfWork."""

    _by_document: dict[str, ExtractionResult] = field(default_factory=dict)
    _by_extraction_id: dict[str, ExtractionResult] = field(default_factory=dict)
    _relationships_by_document: dict[str, list[SemanticRelationship]] = field(
        default_factory=dict
    )

    def save_extraction_result(self, result: ExtractionResult) -> None:
        self._by_document[result.document_id] = result
        self._by_extraction_id[result.extraction_id] = result

    def replace_extraction_result(self, result: ExtractionResult) -> None:
        self.save_extraction_result(result)

    def delete_by_document(self, document_id: str) -> None:
        existing = self._by_document.pop(document_id, None)
        if existing is not None:
            self._by_extraction_id.pop(existing.extraction_id, None)
        self._relationships_by_document.pop(document_id, None)

    def get_extraction_result(self, extraction_id: str) -> ExtractionResult | None:
        return self._by_extraction_id.get(extraction_id)

    def get_document_extraction_result(
        self, document_id: str
    ) -> ExtractionResult | None:
        return self._by_document.get(document_id)

    def has_extraction_result(self, document_id: str) -> bool:
        return document_id in self._by_document

    def _list(self, document_id: str | None, attribute: str) -> list[Any]:
        if document_id is not None:
            result = self._by_document.get(document_id)
            return list(getattr(result, attribute)) if result is not None else []
        items: list[Any] = []
        for result in self._by_document.values():
            items.extend(getattr(result, attribute))
        return items

    def list_maintenance_tasks(
        self, document_id: str | None = None
    ) -> list[MaintenanceTask]:
        return self._list(document_id, "maintenance_tasks")

    def list_spare_parts(self, document_id: str | None = None) -> list[SparePart]:
        return self._list(document_id, "spare_parts")

    def list_equipment(self, document_id: str | None = None) -> list[EquipmentInfo]:
        return self._list(document_id, "equipment")

    def list_manufacturers(self, document_id: str | None = None) -> list[Manufacturer]:
        return self._list(document_id, "manufacturers")

    def list_suppliers(self, document_id: str | None = None) -> list[Supplier]:
        return self._list(document_id, "suppliers")

    def list_contact_points(self, document_id: str | None = None) -> list[ContactPoint]:
        return self._list(document_id, "contact_points")

    def list_procedures(self, document_id: str | None = None) -> list[Procedure]:
        return self._list(document_id, "procedures")

    def list_specifications(self, document_id: str | None = None) -> list[Specification]:
        return self._list(document_id, "specifications")

    def list_safety_warnings(self, document_id: str | None = None) -> list[SafetyWarning]:
        return self._list(document_id, "safety_warnings")

    def list_maintenance_intervals(
        self, document_id: str | None = None
    ) -> list[MaintenanceInterval]:
        return self._list(document_id, "maintenance_intervals")

    def list_troubleshooting_entries(
        self, document_id: str | None = None
    ) -> list[TroubleshootingEntry]:
        return self._list(document_id, "troubleshooting_entries")

    def search_maintenance_tasks(
        self, query: str, document_id: str | None = None
    ) -> list[MaintenanceTask]:
        return [
            task
            for task in self.list_maintenance_tasks(document_id)
            if query.lower() in (task.title or "").lower()
        ]

    def search_spare_parts(
        self, query: str, document_id: str | None = None
    ) -> list[SparePart]:
        return [
            part
            for part in self.list_spare_parts(document_id)
            if query.lower() in (part.description or "").lower()
        ]

    def search_equipment(
        self, query: str, document_id: str | None = None
    ) -> list[EquipmentInfo]:
        return [
            item
            for item in self.list_equipment(document_id)
            if query.lower() in (item.name or "").lower()
        ]

    def search_manufacturers(
        self, query: str, document_id: str | None = None
    ) -> list[Manufacturer]:
        return [
            item
            for item in self.list_manufacturers(document_id)
            if query.lower() in (item.name or "").lower()
        ]

    def search_suppliers(
        self, query: str, document_id: str | None = None
    ) -> list[Supplier]:
        return [
            item
            for item in self.list_suppliers(document_id)
            if query.lower() in (item.name or "").lower()
        ]

    def search_contact_points(
        self, query: str, document_id: str | None = None
    ) -> list[ContactPoint]:
        return [
            item
            for item in self.list_contact_points(document_id)
            if query.lower() in (item.value or "").lower()
        ]

    def search_procedures(
        self, query: str, document_id: str | None = None
    ) -> list[Procedure]:
        return [
            item
            for item in self.list_procedures(document_id)
            if query.lower() in (item.title or "").lower()
        ]

    def search_specifications(
        self, query: str, document_id: str | None = None
    ) -> list[Specification]:
        return [
            item
            for item in self.list_specifications(document_id)
            if query.lower() in (item.parameter or "").lower()
        ]

    def search_safety_warnings(
        self, query: str, document_id: str | None = None
    ) -> list[SafetyWarning]:
        return [
            item
            for item in self.list_safety_warnings(document_id)
            if query.lower() in (item.message or "").lower()
        ]

    def search_maintenance_intervals(
        self, query: str, document_id: str | None = None
    ) -> list[MaintenanceInterval]:
        return [
            item
            for item in self.list_maintenance_intervals(document_id)
            if query.lower() in (item.interval or "").lower()
        ]

    def search_troubleshooting_entries(
        self, query: str, document_id: str | None = None
    ) -> list[TroubleshootingEntry]:
        return [
            item
            for item in self.list_troubleshooting_entries(document_id)
            if query.lower() in (item.symptom or "").lower()
        ]

    def list_maintenance_intervals_by_task_id(
        self, maintenance_task_id: str
    ) -> list[MaintenanceInterval]:
        return [
            interval
            for interval in self.list_maintenance_intervals()
            if interval.maintenance_task_id == maintenance_task_id
        ]

    def list_procedures_by_equipment_id(self, equipment_id: str) -> list[Procedure]:
        return [
            procedure
            for procedure in self.list_procedures()
            if procedure.equipment_id == equipment_id
        ]

    def list_troubleshooting_entries_by_equipment_id(
        self, equipment_id: str
    ) -> list[TroubleshootingEntry]:
        return [
            entry
            for entry in self.list_troubleshooting_entries()
            if entry.equipment_id == equipment_id
        ]

    def list_semantic_relationships(
        self, document_id: str | None = None
    ) -> list[SemanticRelationship]:
        if document_id is not None:
            return list(self._relationships_by_document.get(document_id, []))
        items: list[SemanticRelationship] = []
        for relationships in self._relationships_by_document.values():
            items.extend(relationships)
        return items

    def replace_semantic_relationships(
        self, document_id: str, relationships: list[SemanticRelationship]
    ) -> None:
        self._relationships_by_document[document_id] = list(relationships)


def _assert_protocol_satisfied() -> None:
    """Static-ish safety net: fails fast at import time if
    `InMemoryExtractionRepository` ever drifts from the real
    `ExtractionRepository` Protocol (e.g. a new method added to production)."""
    _repository: ExtractionRepository = InMemoryExtractionRepository()
    del _repository


_assert_protocol_satisfied()


__all__ = [
    "RecordedLLMCall",
    "CannedResponseLLMService",
    "InMemoryExtractionRepository",
]
