from typing import Protocol

from src.domain.activity import ActivityRecord


class ActivityRepository(Protocol):
    def save(self, activity: ActivityRecord) -> None:
        ...

    def list_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 50,
    ) -> list[ActivityRecord]:
        ...