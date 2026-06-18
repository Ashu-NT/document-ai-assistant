from src.domain.activity import ActivityRecord


def test_activity_repository_saves_and_lists_by_entity(db_uow) -> None:
    activity = ActivityRecord(
        action="document.uploaded",
        message="Document uploaded.",
        entity_type="document",
        entity_id="doc_001",
        payload={"file_name": "manual.pdf"},
    )

    db_uow.activity.save(activity)
    db_uow.commit()

    activities = db_uow.activity.list_by_entity(
        entity_type="document",
        entity_id="doc_001",
    )

    assert len(activities) == 1
    assert activities[0].action == "document.uploaded"