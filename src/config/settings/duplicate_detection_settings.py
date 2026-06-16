from pydantic import Field
from pydantic_settings import BaseSettings


class DuplicateDetectionSettings(BaseSettings):
    enable_file_hash_check: bool = Field(
        alias="ENABLE_FILE_HASH_CHECK"
    )

    enable_content_hash_check: bool = Field(
        alias="ENABLE_CONTENT_HASH_CHECK"
    )

    content_hash_normalize_text: bool = Field(
        alias="CONTENT_HASH_NORMALIZE_TEXT"
    )

    class Config:
        env_file = ".env"
        