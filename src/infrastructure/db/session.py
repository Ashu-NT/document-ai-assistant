from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.settings import database_settings


engine = create_engine(
    database_settings.database_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)