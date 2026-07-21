from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.application.langgraph.evaluation.agent_test_case import AgentTestCase
from src.application.langgraph.evaluation.loading.agent_eval_case_parser import (
    extract_case_items,
    parse_case,
    validate_unique_case_ids,
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
        case_items = extract_case_items(payload, source_path=source_path)
        cases = [
            parse_case(item, source_path=source_path, case_index=index)
            for index, item in enumerate(case_items, start=1)
        ]
        validate_unique_case_ids(cases, source_path=source_path)
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
