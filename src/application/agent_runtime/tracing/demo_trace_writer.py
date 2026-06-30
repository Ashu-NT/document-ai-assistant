from __future__ import annotations

from datetime import datetime
from pathlib import Path


class DemoTraceWriter:
    def __init__(
        self,
        *,
        markdown_presenter,
        json_presenter,
        output_dir: Path | str = "outputs/demo_agent",
    ) -> None:
        self.markdown_presenter = markdown_presenter
        self.json_presenter = json_presenter
        self.output_dir = Path(output_dir)

    def write_latest_trace(
        self,
        *,
        session,
        result,
        react_trace,
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        markdown_path = self.output_dir / f"demo_trace_{timestamp}.md"
        json_path = self.output_dir / f"demo_trace_{timestamp}.json"
        markdown_path.write_text(
            self.markdown_presenter.render(
                session=session,
                result=result,
                react_trace=react_trace,
            ),
            encoding="utf-8",
        )
        json_payload = self.json_presenter.to_payload(
            session=session,
            result=result,
            react_trace=react_trace,
            include_trace=True,
        )
        json_path.write_text(
            __import__("json").dumps(json_payload, indent=2),
            encoding="utf-8",
        )
        return {
            "markdown_path": str(markdown_path),
            "json_path": str(json_path),
        }
