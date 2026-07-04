from src.application.tools.documents import FindDocumentRequest
from src.application.tools.question_answering import (
    AnswerQuestionRequest,
    AnswerQuestionTool,
)
from src.application.workflows.question_answering import (
    QuestionAnsweringResult,
    QuestionAnsweringRoute,
)


class FakeQuestionAnsweringWorkflow:
    def __init__(self) -> None:
        self.requests = []
        self.progress_callbacks = []

    def run(self, request, *, progress_callback=None):
        self.requests.append(request)
        self.progress_callbacks.append(progress_callback)
        return QuestionAnsweringResult(
            route=QuestionAnsweringRoute.RETRIEVAL_QA,
            answer_text="The maintenance interval is 500 hours.",
            confidence="0.92",
        )


class FakeFindDocumentTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request: FindDocumentRequest):
        self.requests.append(request)
        return type(
            "FindResult",
            (),
            {
                "success": True,
                "data": {"document_id": "doc-42", "display_name": "Pump Manual"},
                "message": None,
                "error_code": None,
                "diagnostics": {},
            },
        )()


def test_answer_question_tool_resolves_alias_and_delegates_to_workflow():
    workflow = FakeQuestionAnsweringWorkflow()
    find_tool = FakeFindDocumentTool()
    tool = AnswerQuestionTool(workflow, find_document_tool=find_tool)

    result = tool.run(
        AnswerQuestionRequest(
            question="What is the maintenance interval?",
            document_alias="Pump",
            top_k=3,
        )
    )

    assert result.success is True
    assert find_tool.requests[0].query_text == "Pump"
    assert workflow.requests[0].document_id == "doc-42"
    assert result.data.answer_text == "The maintenance interval is 500 hours."


def test_answer_question_tool_forwards_progress_callback_to_workflow():
    workflow = FakeQuestionAnsweringWorkflow()
    tool = AnswerQuestionTool(workflow)
    messages: list[str] = []

    tool.run(
        AnswerQuestionRequest(
            question="What is the maintenance interval?",
            document_id="doc-42",
            progress_callback=messages.append,
        )
    )

    assert workflow.progress_callbacks[0] == messages.append


def test_answer_question_tool_defaults_progress_callback_to_none():
    workflow = FakeQuestionAnsweringWorkflow()
    tool = AnswerQuestionTool(workflow)

    tool.run(
        AnswerQuestionRequest(question="What is the maintenance interval?", document_id="doc-42")
    )

    assert workflow.progress_callbacks[0] is None
