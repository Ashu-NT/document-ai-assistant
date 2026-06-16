from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    database_provider: str = Field(alias="DATABASE_PROVIDER")
    database_url: str = Field(alias="DATABASE_URL")

    class Config:
        env_file = ".env"
        extra = "ignore"
        