from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.nodes.evaluation import RunQualityGateNode
from src.application.langgraph.state import build_agent_state
from src.application.tools.common import ToolResult


class FakeRunQualityGateTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return ToolResult.ok(
            data={"summary": "Quality gate passed.", "passed": True}
        )


def test_run_quality_gate_node_calls_quality_gate_tool() -> None:
    tool = FakeRunQualityGateTool()
    node = RunQualityGateNode(ToolRegistry(run_quality_gate_tool=tool))

    patch = node(build_agent_state(user_input="run quality gate"))

    assert tool.requests
    assert patch["response_text"] == "Quality gate passed."
