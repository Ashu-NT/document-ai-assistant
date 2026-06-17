from pathlib import Path

from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings

from src.config.paths import resolve_project_path


class StorageSettings(AppBaseSettings):
    project_root: str | None = Field(default=None, alias="PROJECT_ROOT")

    data_dir: str = Field(alias="DATA_DIR")
    input_dir: str = Field(alias="INPUT_DIR")
    output_dir: str = Field(alias="OUTPUT_DIR")
    parsed_output_dir: str = Field(alias="PARSED_OUTPUT_DIR")
    image_output_dir: str = Field(alias="IMAGE_OUTPUT_DIR")
    export_output_dir: str = Field(alias="EXPORT_OUTPUT_DIR")
    evaluation_output_dir: str = Field(alias="EVALUATION_OUTPUT_DIR")
    log_dir: str = Field(alias="LOG_DIR")


    @property
    def data_path(self) -> Path:
        return resolve_project_path(self.data_dir)

    @property
    def input_path(self) -> Path:
        return resolve_project_path(self.input_dir)

    @property
    def output_path(self) -> Path:
        return resolve_project_path(self.output_dir)

    @property
    def parsed_output_path(self) -> Path:
        return resolve_project_path(self.parsed_output_dir)

    @property
    def image_output_path(self) -> Path:
        return resolve_project_path(self.image_output_dir)

    @property
    def export_output_path(self) -> Path:
        return resolve_project_path(self.export_output_dir)

    @property
    def evaluation_output_path(self) -> Path:
        return resolve_project_path(self.evaluation_output_dir)

    @property
    def log_path(self) -> Path:
        return resolve_project_path(self.log_dir)

    def ensure_directories(self) -> None:
        for path in [
            self.data_path,
            self.input_path,
            self.output_path,
            self.parsed_output_path,
            self.image_output_path,
            self.export_output_path,
            self.evaluation_output_path,
            self.log_path,
        ]:
            path.mkdir(parents=True, exist_ok=True)