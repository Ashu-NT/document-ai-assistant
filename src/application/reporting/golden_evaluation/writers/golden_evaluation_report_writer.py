import json
from pathlib import Path

from src.application.evaluation.golden.golden_evaluation_report import (
    GoldenEvaluationReport,
)
from src.application.reporting.golden_evaluation.renderers.golden_evaluation_report_markdown_renderer import (
    GoldenEvaluationReportMarkdownRenderer,
)
from src.application.reporting.golden_evaluation.serializers.golden_evaluation_report_json_serializer import (
    GoldenEvaluationReportJsonSerializer,
)


class GoldenEvaluationReportWriter:
    def __init__(
        self,
        *,
        json_serializer: GoldenEvaluationReportJsonSerializer | None = None,
        markdown_renderer: GoldenEvaluationReportMarkdownRenderer | None = None,
    ) -> None:
        self.json_serializer = json_serializer or GoldenEvaluationReportJsonSerializer()
        self.markdown_renderer = markdown_renderer or GoldenEvaluationReportMarkdownRenderer()

    def write_json(
        self,
        report: GoldenEvaluationReport,
        output_path: Path | str,
    ) -> Path:
        resolved_path = Path(output_path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(
            json.dumps(self.json_serializer.serialize(report), indent=2, default=str),
            encoding="utf-8",
        )
        return resolved_path

    def write_markdown(
        self,
        report: GoldenEvaluationReport,
        output_path: Path | str,
    ) -> Path:
        resolved_path = Path(output_path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(
            self.markdown_renderer.render(report),
            encoding="utf-8",
        )
        return resolved_path


__all__ = ["GoldenEvaluationReportWriter"]
