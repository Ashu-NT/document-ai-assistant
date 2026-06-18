from dataclasses import asdict, is_dataclass
from typing import Any

from src.domain.events import DomainEvent


_RESERVED_FIELDS = {
    "event_id",
    "event_type",
    "aggregate_id",
    "aggregate_type",
    "occurred_at",
}


class DomainEventSerializer:
    @staticmethod
    def to_payload(event: DomainEvent) -> dict[str, Any]:
        if not is_dataclass(event):
            return {}

        data = asdict(event)

        return {
            key: value
            for key, value in data.items()
            if key not in _RESERVED_FIELDS and value is not None
        }