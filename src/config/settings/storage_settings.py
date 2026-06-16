from pydantic import Field
from pydantic_settings import BaseSettings


class StorageSettings(BaseSettings):

    input_dir: str = Field(alias="INPUT_DIR")

    output_dir: str = Field(alias="OUTPUT_DIR")

    parsed_output_dir: str = Field(
        alias="PARSED_OUTPUT_DIR"
    )

    image_output_dir: str = Field(
        alias="IMAGE_OUTPUT_DIR"
    )

    export_output_dir: str = Field(
        alias="EXPORT_OUTPUT_DIR"
    )

    evaluation_output_dir: str = Field(
        alias="EVALUATION_OUTPUT_DIR"
    )

    class Config:
        env_file = ".env"
