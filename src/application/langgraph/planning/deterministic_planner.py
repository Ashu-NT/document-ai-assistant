from __future__ import annotations

from src.application.langgraph.planning.compare_plan_builder import build_compare_plan
from src.application.langgraph.planning.compound_request_classifier import (
    is_compare_request,
    is_explore_and_answer_request,
    is_list_and_find_request,
    is_retrieve_and_answer_request,
    looks_compound,
)
from src.application.langgraph.planning.deterministic.identifier_plan_builder import (
    build_identifier_plan,
    extract_identifier_value,
    has_identifier_term,
)
from src.application.langgraph.planning.execution_plan import ExecutionPlan
from src.application.langgraph.planning.explore_and_retrieve_plan_builders import (
    build_explore_and_answer_plan,
    build_retrieve_and_answer_plan,
)
from src.application.langgraph.planning.list_and_find_plan_builder import (
    build_list_and_find_plan,
)
from src.application.langgraph.planning.structured_entity_plan_builder import (
    build_structured_entity_plan,
    extract_structured_entity_type,
)
from src.application.langgraph.state import AgentState
from src.shared.ids import IdGenerator


class DeterministicPlanner:
    def __init__(self, *, id_generator: IdGenerator | None = None) -> None:
        self.id_generator = id_generator or IdGenerator()

    def create_plan(self, state: AgentState) -> ExecutionPlan | None:
        normalized_input = self._normalize(
            state.get("question") or state.get("user_input") or ""
        )

        explicit_document_id = state.get("document_id")
        selected_document_id = state.get("selected_document_id")
        document_query = state.get("document_query")
        document_id = explicit_document_id or selected_document_id
        document_title = state.get("document_title") or state.get("selected_document_title")

        structured_entity_type = extract_structured_entity_type(normalized_input)
        if structured_entity_type:
            return build_structured_entity_plan(
                self.id_generator,
                normalized_input=normalized_input,
                entity_type=structured_entity_type,
                document_query=document_query,
                document_id=document_id,
                document_title=document_title,
            )

        identifier_value = extract_identifier_value(normalized_input)
        if identifier_value or has_identifier_term(normalized_input):
            return build_identifier_plan(
                self.id_generator,
                normalized_input=normalized_input,
                identifier_value=identifier_value,
                document_query=document_query,
                document_id=document_id,
                document_title=document_title,
            )

        if not looks_compound(normalized_input):
            return None

        if is_list_and_find_request(normalized_input):
            return build_list_and_find_plan(
                self.id_generator,
                normalized_input=normalized_input,
                document_query=document_query,
                document_id=document_id,
                document_title=document_title,
            )

        if is_compare_request(normalized_input):
            return build_compare_plan(
                self.id_generator,
                normalized_input=normalized_input,
                document_query=document_query,
                document_id=document_id,
                document_title=document_title,
            )

        if is_explore_and_answer_request(normalized_input):
            return build_explore_and_answer_plan(
                self.id_generator,
                normalized_input=normalized_input,
                document_query=document_query,
                document_id=document_id,
                document_title=document_title,
            )

        if is_retrieve_and_answer_request(normalized_input):
            return build_retrieve_and_answer_plan(
                self.id_generator,
                normalized_input=normalized_input,
                document_query=document_query,
                document_id=document_id,
                document_title=document_title,
            )
        return None

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.strip().lower().split())
