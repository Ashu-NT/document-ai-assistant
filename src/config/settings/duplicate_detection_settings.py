from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class DuplicateDetectionSettings(AppBaseSettings):
    enable_file_hash_check: bool = Field(
        alias="ENABLE_FILE_HASH_CHECK"
    )

    enable_content_hash_check: bool = Field(
        alias="ENABLE_CONTENT_HASH_CHECK"
    )
