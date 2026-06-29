from enum import StrEnum


class RouteType(StrEnum):
    SELECT_DOCUMENT = "select_document"
    CURRENT_DOCUMENT = "current_document"
    CLEAR_DOCUMENT = "clear_document"
    CLARIFICATION_RESPONSE = "clarification_response"
    HELP = "help"
    EXIT = "exit"
    LIST_DOCUMENTS = "list_documents"
    FIND_DOCUMENT = "find_document"
    DOCUMENT_DETAILS = "document_details"
    DOCUMENT_EXPLORATION = "document_exploration"
    RETRIEVE_EVIDENCE = "retrieve_evidence"
    ANSWER_QUESTION = "answer_question"
    QUALITY_GATE = "quality_gate"
    RETRIEVAL_TRACE = "retrieval_trace"
    NEEDS_CLARIFICATION = "needs_clarification"
    UNKNOWN = "unknown"
