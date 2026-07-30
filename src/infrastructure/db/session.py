from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.config.settings import database_settings


engine = create_engine(
    database_settings.resolved_database_url,
    pool_pre_ping=True,
    future=True,
)

if engine.dialect.name == "sqlite":
    # SQLite ignores FOREIGN KEY constraints by default per connection;
    # without this, ondelete= policies declared on the ORM models are
    # silently no-ops and orphaned child rows are never prevented.
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)