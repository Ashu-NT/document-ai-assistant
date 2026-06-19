from collections.abc import Sequence
from typing import Any

from src.shared.execution.action_result import ActionResult


class ResultAdapter:
    @staticmethod
    def to_action_result(
        result: Any,
        *,
        default_entity_type: str | None = None,
    ) -> ActionResult:
        if isinstance(result, ActionResult):
            return result

        if isinstance(result, Sequence) and not isinstance(
            result,
            (str, bytes, bytearray),
        ):
            return ActionResult(
                entity_type=default_entity_type,
                payload={
                    "result_count": len(result),
                    "result_type": "list",
                },
            )

        return ActionResult(
            entity_type=default_entity_type,
            payload={
                "result_type": type(result).__name__,
            },
        )
