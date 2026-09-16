import importlib.util
from pathlib import Path
from types import ModuleType

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Column, MetaData, String, Table, create_engine, inspect, text

_MIGRATION_PATH = (
    Path(__file__).resolve().parents[5]
    / "alembic"
    / "versions"
    / "9e3639e37418_add_target_annex_label_to_chunk_cross_references_and_evidence.py"
)


def _load_migration_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "add_target_annex_label_migration", _MIGRATION_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_pre_migration_tables(engine) -> None:
    """Minimal pre-migration schema for just the two affected tables -
    enough to run this migration's upgrade()/downgrade() in isolation and
    prove existing rows survive, without replaying the full migration
    history (the two tables' full column sets are exercised by the ORM
    models/schema_management, not by this migration-specific test)."""
    metadata = MetaData()
    Table("chunk_cross_references", metadata, Column("id", String, primary_key=True))
    Table(
        "chunk_cross_reference_evidence",
        metadata,
        Column("id", String, primary_key=True),
    )
    metadata.create_all(engine)


def test_migration_file_revision_matches_filename() -> None:
    module = _load_migration_module()

    assert module.revision == "9e3639e37418"
    assert module.down_revision == "c9d3f6a1e2b7"


def test_upgrade_adds_nullable_target_annex_label_columns_and_preserves_existing_rows() -> (
    None
):
    module = _load_migration_module()
    engine = create_engine("sqlite:///:memory:", future=True)
    _build_pre_migration_tables(engine)

    with engine.connect() as connection:
        # Simulate rows that existed before this migration ran.
        connection.execute(
            text("INSERT INTO chunk_cross_references (id) VALUES ('xref_pre_existing')")
        )
        connection.execute(
            text(
                "INSERT INTO chunk_cross_reference_evidence (id) "
                "VALUES ('evidence_pre_existing')"
            )
        )
        connection.commit()

        migration_context = MigrationContext.configure(connection)
        with Operations.context(migration_context):
            module.upgrade()
        connection.commit()

        inspector = inspect(connection)
        xref_columns = {c["name"] for c in inspector.get_columns("chunk_cross_references")}
        evidence_columns = {
            c["name"] for c in inspector.get_columns("chunk_cross_reference_evidence")
        }
        assert "target_annex_label" in xref_columns
        assert "target_annex_label" in evidence_columns

        # Existing database rows must remain valid with NULL - no
        # speculative backfill, no constraint violation.
        pre_existing_xref_label = connection.execute(
            text(
                "SELECT target_annex_label FROM chunk_cross_references "
                "WHERE id = 'xref_pre_existing'"
            )
        ).scalar()
        pre_existing_evidence_label = connection.execute(
            text(
                "SELECT target_annex_label FROM chunk_cross_reference_evidence "
                "WHERE id = 'evidence_pre_existing'"
            )
        ).scalar()
        assert pre_existing_xref_label is None
        assert pre_existing_evidence_label is None

        # New rows can now populate the column.
        connection.execute(
            text(
                "INSERT INTO chunk_cross_references (id, target_annex_label) "
                "VALUES ('xref_annex', 'Annex 2')"
            )
        )
        connection.commit()
        new_row_label = connection.execute(
            text(
                "SELECT target_annex_label FROM chunk_cross_references "
                "WHERE id = 'xref_annex'"
            )
        ).scalar()
        assert new_row_label == "Annex 2"


def test_downgrade_drops_target_annex_label_columns_cleanly() -> None:
    module = _load_migration_module()
    engine = create_engine("sqlite:///:memory:", future=True)
    _build_pre_migration_tables(engine)

    with engine.connect() as connection:
        migration_context = MigrationContext.configure(connection)
        with Operations.context(migration_context):
            module.upgrade()
        connection.commit()

        with Operations.context(migration_context):
            module.downgrade()
        connection.commit()

        inspector = inspect(connection)
        xref_columns = {c["name"] for c in inspector.get_columns("chunk_cross_references")}
        evidence_columns = {
            c["name"] for c in inspector.get_columns("chunk_cross_reference_evidence")
        }
        assert "target_annex_label" not in xref_columns
        assert "target_annex_label" not in evidence_columns
