from sqlalchemy.engine import Engine

from src.infrastructure.db.base import Base


def ensure_database_schema(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)

    if engine.dialect.name != "sqlite":
        return

    _ensure_sqlite_column(
        engine=engine,
        table_name="elements",
        column_name="parser_extra_json",
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
