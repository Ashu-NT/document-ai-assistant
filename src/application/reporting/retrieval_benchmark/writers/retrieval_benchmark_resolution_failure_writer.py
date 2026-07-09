import json
from pathlib import Path
from typing import Any

from src.application.reporting.retrieval_benchmark.renderers import (
    RetrievalBenchmarkResolutionFailureMarkdownRenderer,
)
from src.application.reporting.retrieval_benchmark.serializers import (
    RetrievalBenchmarkResolutionFailureJsonSerializer,
)


class RetrievalBenchmarkResolutionFailureWriter:
    def __init__(
        self,
        *,
        json_serializer: (
            RetrievalBenchmarkResolutionFailureJsonSerializer | None
        ) = None,
        markdown_renderer: (
            RetrievalBenchmarkResolutionFailureMarkdownRenderer | None
        ) = None,
    ) -> None:
        self.json_serializer = (
            json_serializer or RetrievalBenchmarkResolutionFailureJsonSerializer()
        )
        self.markdown_renderer = (
            markdown_renderer
            or RetrievalBenchmarkResolutionFailureMarkdownRenderer()
        )

    def write_json(
        self,
        *,
        details: dict[str, Any] | None,
        output_path: Path | str,
        subset: str,
        truth_set_path: Path | str,
        manifest_path: Path | str,
    ) -> Path:
        resolved_path = Path(output_path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(
            json.dumps(
                self.json_serializer.serialize(
                    details=details,
                    subset=subset,
                    truth_set_path=truth_set_path,
                    manifest_path=manifest_path,
                ),
                indent=2,
            ),
            encoding="utf-8",
        )
        return resolved_path

    def write_markdown(
        self,
        *,
        details: dict[str, Any] | None,
        output_path: Path | str,
        subset: str,
        truth_set_path: Path | str,
        manifest_path: Path | str,
    ) -> Path:
        resolved_path = Path(output_path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(
            self.markdown_renderer.render(
                details=details,
                subset=subset,
                truth_set_path=truth_set_path,
                manifest_path=manifest_path,
            ),
            encoding="utf-8",
        )
        return resolved_path
