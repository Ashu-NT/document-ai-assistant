from src.domain.events import IngestionEvent, ClassificationEvent


def test_ingestion_started_event() -> None:
    event = IngestionEvent.started(
        event_id="event_001",
        ingestion_run_id="run_001",
        document_id="doc_001",
    )

    assert event.event_type == "ingestion.started"
    assert event.document_id == "doc_001"
    assert event.ingestion_run_id == "run_001"


def test_classification_completed_event() -> None:
    event = ClassificationEvent.completed(
        event_id="event_001",
        document_id="doc_001",
        classification_id="class_001",
        predicted_label="manual",
        confidence_score=0.9,
    )

    assert event.event_type == "classification.completed"
    assert event.predicted_label == "manual"