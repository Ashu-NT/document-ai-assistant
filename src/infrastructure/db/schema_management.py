from sqlalchemy.engine import Engine

from src.infrastructure.db.base import Base


def ensure_database_schema(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)

    if engine.dialect.name != "sqlite":
        return

    _ensure_sqlite_column(
        engine=engine,
        table_name="documents",
        column_name="metadata_json",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="documents",
        column_name="parser_version",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunk_cross_references",
        column_name="target_asset_label",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="elements",
        column_name="parser_extra_json",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="sections",
        column_name="raw_section_path",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="sections",
        column_name="normalized_section_path",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="element_ids_json",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="table_ids_json",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="picture_ids_json",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="logical_table_family_id",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="logical_table_family_index",
        column_ddl="INTEGER",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="logical_table_family_total",
        column_ddl="INTEGER",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="logical_table_continuation_role",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="table_category",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="table_category_confidence",
        column_ddl="REAL",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="table_row_start",
        column_ddl="INTEGER",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="table_row_end",
        column_ddl="INTEGER",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="table_shape",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="table_structure_quality",
        column_ddl="REAL",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="header_paths_json",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="chunks",
        column_name="axis_summary_json",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="extraction_results",
        column_name="source_chunk_ids_json",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="extraction_results",
        column_name="attempted_chunk_ids_json",
        column_ddl="TEXT",
    )
    _ensure_sqlite_column(
        engine=engine,
        table_name="extraction_results",
        column_name="unresolved_chunk_ids_json",
        column_ddl="TEXT",
    )


def _ensure_sqlite_column(
    *,
    engine: Engine,
    table_name: str,
    column_name: str,
    column_ddl: str,
) -> None:
    with engine.begin() as connection:
        rows = connection.exec_driver_sql(f"PRAGMA table_info({table_name})").fetchall()
        existing_columns = {str(row[1]) for row in rows}
        if column_name in existing_columns:
            return

        connection.exec_driver_sql(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_ddl}"
        )
