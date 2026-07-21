from pathlib import Path

from src.application.workflows.ingestion.models.ingestion_stage import IngestionStage

_INGESTION_SOURCE_DIR = (
    Path(__file__).resolve().parents[6]
    / "src"
    / "application"
    / "workflows"
    / "ingestion"
)


def test_every_declared_stage_is_actually_reached_by_the_workflow() -> None:
    """Guards against a stage being declared but never wired up.

    `IngestionStage.VALIDATION` used to exist in the enum but was never
    assigned to `current_stage` anywhere in `IngestionWorkflow.run` -
    request validation happens before an `IngestionRun` even exists, so it
    structurally could never be tracked as a run stage. This test fails
    loudly if a future stage is added to the enum without also being wired
    into the workflow (or vice versa - removed from the workflow but left in
    the enum).
    """
    source_parts = []
    for path in _INGESTION_SOURCE_DIR.rglob("*.py"):
        if path.name == "ingestion_stage.py":
            continue
        source_parts.append(path.read_text(encoding="utf-8"))
    source = "\n".join(source_parts)

    unreachable = [
        stage.name
        for stage in IngestionStage
        if f"IngestionStage.{stage.name}" not in source
    ]

    assert unreachable == [], (
        f"IngestionStage member(s) {unreachable} are declared but never "
        "referenced in the ingestion workflow source tree."
    )
