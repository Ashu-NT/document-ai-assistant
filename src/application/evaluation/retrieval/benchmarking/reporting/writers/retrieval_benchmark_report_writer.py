import json
from pathlib import Path

from src.application.evaluation.retrieval.benchmarking.models import (
    RetrievalBenchmarkReport,
)
from src.application.evaluation.retrieval.benchmarking.reporting.renderers import (
    RetrievalBenchmarkReportMarkdownRenderer,
)
from src.application.evaluation.retrieval.benchmarking.reporting.serializers import (
    RetrievalBenchmarkReportJsonSerializer,
)


class RetrievalBenchmarkReportWriter:
    def __init__(
        self,
        *,
        json_serializer: RetrievalBenchmarkReportJsonSerializer | None = None,
        markdown_renderer: (
            RetrievalBenchmarkReportMarkdownRenderer | None
        ) = None,
    ) -> None:
        self.json_serializer = (
            json_serializer or RetrievalBenchmarkReportJsonSerializer()
        )
        self.markdown_renderer = (
            markdown_renderer or RetrievalBenchmarkReportMarkdownRenderer()
        )

    def write_json(
        self,
        report: RetrievalBenchmarkReport,
        output_path: Path | str,
    ) -> Path:
        resolved_path = Path(output_path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(
            json.dumps(
                self.json_serializer.serialize(report),
                indent=2,
            ),
            encoding="utf-8",
        )
        return resolved_path

    def write_markdown(
        self,
        report: RetrievalBenchmarkReport,
        output_path: Path | str,
    ) -> Path:
        resolved_path = Path(output_path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(
            self.markdown_renderer.render(report),
            encoding="utf-8",
        )
        return resolved_path
