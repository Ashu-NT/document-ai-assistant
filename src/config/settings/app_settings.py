from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings

class AppSettings(AppBaseSettings):
    app_name: str = Field(alias="APP_NAME")
    app_env: str = Field(alias="APP_ENV")
    app_debug: bool = Field(alias="APP_DEBUG")
        