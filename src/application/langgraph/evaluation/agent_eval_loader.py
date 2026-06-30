from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.application.langgraph.evaluation.agent_test_case import (
    AgentExpectedBehavior,
    AgentTestCase,
    AgentTurnInput,
)
from src.shared.exceptions import SchemaValidationError

DEFAULT_AGENT_EVAL_CASES_PATH = Path("src/config/evaluation/agent_eval_cases.yaml")


class AgentEvalLoader:
    def load(self, path: Path | str | None = None) -> list[AgentTestCase]:
        source_path = self.resolve_path(path)
        if not source_path.exists():
            raise SchemaValidationError(
                "Agent evaluation case file not found.",
                details={"path": str(source_path)},
            )

        payload = self._load_payload(source_path)
        case_items = self._extract_case_items(payload, source_path=source_path)
        cases = [
            self._parse_case(item, source_path=source_path, case_index=index)
            for index, item in enumerate(case_items, start=1)
        ]
        self._validate_unique_case_ids(cases, source_path=source_path)
        return cases

    @staticmethod
    def resolve_path(path: Path | str | None = None) -> Path:
        if path is None:
            return DEFAULT_AGENT_EVAL_CASES_PATH
        return Path(path)

    def _load_payload(self, source_path: Path) -> Any:
        if source_path.suffix.lower() == ".json":
            return json.loads(source_path.read_text(encoding="utf-8"))

        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:
            raise SchemaValidationError(
                "PyYAML is required to load agent evaluation YAML files.",
                details={"path": str(source_path)},
            ) from exc

        return yaml.safe_load(source_path.read_text(encoding="utf-8"))

    def _extract_case_items(
        self,
        payload: Any,
        *,
        source_path: Path,
    ) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            case_items = payload
        elif isinstance(payload, dict) and isinstance(payload.get("cases"), list):
            case_items = payload["cases"]
        else:
            raise SchemaValidationError(
                "Agent evaluation case file must contain a list of cases.",
                details={"path": str(source_path)},
            )

        if not case_items:
            raise SchemaValidationError(
                "Agent evaluation case file did not contain any cases.",
                details={"path": str(source_path)},
            )
        if not all(isinstance(item, dict) for item in case_items):
            raise SchemaValidationError(
                "Each agent evaluation case must be a mapping.",
                details={"path": str(source_path)},
            )
        return case_items

    def _parse_case(
        self,
        payload: dict[str, Any],
        *,
        source_path: Path,
        case_index: int,
    ) -> AgentTestCase:
        case_id = self._required_string(
            payload,
            "case_id",
            source_path=source_path,
            case_index=case_index,
        )
        name = self._required_string(
            payload,
            "name",
            source_path=source_path,
            case_index=case_index,
        )
        inputs_payload = payload.get("inputs")
        if not isinstance(inputs_payload, list) or not inputs_payload:
            raise SchemaValidationError(
                "Agent evaluation case inputs must be a non-empty list.",
                details={
                    "path": str(source_path),
                    "case_index": case_index,
                    "case_id": case_id,
                },
            )

        expected_payload = payload.get("expected")
        if not isinstance(expected_payload, dict):
            raise SchemaValidationError(
                "Agent evaluation case expected behavior must be a mapping.",
                details={
                    "path": str(source_path),
                    "case_index": case_index,
                    "case_id": case_id,
                },
            )

        try:
            return AgentTestCase(
                case_id=case_id,
                name=name,
                description=self._optional_string(payload.get("description")),
                inputs=[
                    self._parse_turn(
                        item,
                        source_path=source_path,
                        case_index=case_index,
                        turn_index=turn_index,
                        case_id=case_id,
                    )
                    for turn_index, item in enumerate(inputs_payload, start=1)
                ],
                expected=self._parse_expected(
                    expected_payload,
                    source_path=source_path,
                    case_index=case_index,
                    case_id=case_id,
                ),
                tags=self._string_list(payload.get("tags")),
                metadata=self._mapping(payload.get("metadata")),
            )
        except ValueError as exc:
            raise SchemaValidationError(
                "Agent evaluation case contains invalid field values.",
                details={
                    "path": str(source_path),
                    "case_index": case_index,
                    "case_id": case_id,
                },
            ) from exc

    def _parse_turn(
        self,
        payload: Any,
        *,
        source_path: Path,
        case_index: int,
        turn_index: int,
        case_id: str,
    ) -> AgentTurnInput:
        if not isinstance(payload, dict):
            raise SchemaValidationError(
                "Agent evaluation turn input must be a mapping.",
                details={
                    "path": str(source_path),
                    "case_index": case_index,
                    "case_id": case_id,
                    "turn_index": turn_index,
                },
            )

        user_input = self._required_string(
            payload,
            "user_input",
            source_path=source_path,
            case_index=case_index,
            case_id=case_id,
            turn_index=turn_index,
        )
        return AgentTurnInput(
            user_input=user_input,
            document=self._optional_string(payload.get("document")),
            document_id=self._optional_string(payload.get("document_id")),
            allow_answer_generation=self._bool_value(
                payload.get("allow_answer_generation"),
                default=False,
            ),
            llm_planning_enabled=self._bool_value(
                payload.get("llm_planning_enabled"),
                default=False,
            ),
            deep_research_enabled=self._bool_value(
                payload.get("deep_research_enabled"),
                default=False,
            ),
            llm_research_planning_enabled=self._bool_value(
                payload.get("llm_research_planning_enabled"),
                default=False,
            ),
            retrieval_strategy_enabled=self._bool_value(
                payload.get("retrieval_strategy_enabled"),
                default=False,
            ),
            llm_retrieval_strategy_enabled=self._bool_value(
                payload.get("llm_retrieval_strategy_enabled"),
                default=False,
            ),
            requested_retrieval_strategy=self._optional_string(
                payload.get("requested_retrieval_strategy")
            ),
            show_retrieval_strategy=self._bool_value(
                payload.get("show_retrieval_strategy"),
                default=False,
            ),
            show_context=self._bool_value(
                payload.get("show_context"),
                default=False,
            ),
            show_plan=self._bool_value(
                payload.get("show_plan"),
                default=False,
            ),
            show_research_plan=self._bool_value(
                payload.get("show_research_plan"),
                default=False,
            ),
            show_research_trace=self._bool_value(
                payload.get("show_research_trace"),
                default=False,
            ),
        )

    def _parse_expected(
        self,
        payload: dict[str, Any],
        *,
        source_path: Path,
        case_index: int,
        case_id: str,
    ) -> AgentExpectedBehavior:
        try:
            return AgentExpectedBehavior(
                final_route=self._optional_string(payload.get("final_route")),
                selected_document_contains=self._optional_string(
                    payload.get("selected_document_contains")
                ),
                selected_document_id=self._optional_string(
                    payload.get("selected_document_id")
                ),
                should_clarify=self._optional_bool(payload.get("should_clarify")),
                should_exit=self._optional_bool(payload.get("should_exit")),
                required_tools=self._string_list(payload.get("required_tools")),
                forbidden_tools=self._string_list(payload.get("forbidden_tools")),
                required_plan_tools=self._string_list(
                    payload.get("required_plan_tools")
                ),
                forbidden_plan_tools=self._string_list(
                    payload.get("forbidden_plan_tools")
                ),
                answer_must_contain=self._string_list(
                    payload.get("answer_must_contain")
                ),
                answer_must_not_contain=self._string_list(
                    payload.get("answer_must_not_contain")
                ),
                context_document_id=self._optional_string(
                    payload.get("context_document_id")
                ),
                unsafe_request_blocked=self._optional_bool(
                    payload.get("unsafe_request_blocked")
                ),
                success=self._optional_bool(payload.get("success")),
                retrieval_strategy_primary=self._optional_string(
                    payload.get("retrieval_strategy_primary")
                ),
                retrieval_strategy_secondary_contains=self._string_list(
                    payload.get("retrieval_strategy_secondary_contains")
                ),
                retrieval_strategy_trace_required=self._optional_bool(
                    payload.get("retrieval_strategy_trace_required")
                ),
                research_plan_required=self._optional_bool(
                    payload.get("research_plan_required")
                ),
                research_report_required=self._optional_bool(
                    payload.get("research_report_required")
                ),
                research_gap_detection_required=self._optional_bool(
                    payload.get("research_gap_detection_required")
                ),
                research_citation_required=self._optional_bool(
                    payload.get("research_citation_required")
                ),
                research_task_success_min_rate=self._optional_float(
                    payload.get("research_task_success_min_rate")
                ),
            )
        except ValueError as exc:
            raise SchemaValidationError(
                "Agent evaluation expected behavior contains invalid values.",
                details={
                    "path": str(source_path),
                    "case_index": case_index,
                    "case_id": case_id,
                },
            ) from exc

    def _validate_unique_case_ids(
        self,
        cases: list[AgentTestCase],
        *,
        source_path: Path,
    ) -> None:
        seen: set[str] = set()
        duplicates: list[str] = []
        for case in cases:
            if case.case_id in seen:
                duplicates.append(case.case_id)
                continue
            seen.add(case.case_id)
        if duplicates:
            raise SchemaValidationError(
                "Agent evaluation case IDs must be unique.",
                details={
                    "path": str(source_path),
                    "duplicate_case_ids": sorted(set(duplicates)),
                },
            )

    def _required_string(
        self,
        payload: dict[str, Any],
        key: str,
        *,
        source_path: Path,
        case_index: int,
        case_id: str | None = None,
        turn_index: int | None = None,
    ) -> str:
        value = self._optional_string(payload.get(key))
        if value is not None:
            return value
        details: dict[str, Any] = {
            "path": str(source_path),
            "case_index": case_index,
            "missing_field": key,
        }
        if case_id is not None:
            details["case_id"] = case_id
        if turn_index is not None:
            details["turn_index"] = turn_index
        raise SchemaValidationError(
            "Agent evaluation case is missing a required string field.",
            details=details,
        )

    @staticmethod
    def _optional_string(value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Expected string value.")
        normalized = value.strip()
        return normalized or None

    @classmethod
    def _string_list(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("Expected list value.")
        result: list[str] = []
        for item in value:
            normalized = cls._optional_string(item)
            if normalized is None:
                continue
            result.append(normalized)
        return result

    @staticmethod
    def _mapping(value: Any) -> dict[str, Any]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError("Expected mapping value.")
        return dict(value)

    @staticmethod
    def _bool_value(value: Any, *, default: bool) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        raise ValueError("Expected boolean value.")

    @staticmethod
    def _optional_bool(value: Any) -> bool | None:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        raise ValueError("Expected boolean or null value.")

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        if value is None:
            return None
        if isinstance(value, int | float):
            return float(value)
        raise ValueError("Expected numeric or null value.")
