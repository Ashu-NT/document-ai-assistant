from __future__ import annotations

from collections.abc import Sequence

from src.application.langgraph.planning.execution_plan import ExecutionPlan
from src.application.langgraph.planning.plan_step import PlanStep
from src.application.langgraph.state import AgentState
from src.shared.ids import IdGenerator

_COMPOUND_MARKERS = (
    " and ",
    " compare ",
    " then ",
    " also ",
    "summarize evidence",
    "retrieve evidence",
)
_TASK_KEYWORDS = (
    "explore",
    "retrieve",
    "evidence",
    "summarize",
    "compare",
    "specification",
    "maintenance",
    "safety",
    "procedure",
    "sections",
    "tables",
)
_COMPARISON_TOPICS: tuple[tuple[str, str, str], ...] = (
    ("specification", "Specifications", "What specifications are available in this document?"),
    ("maintenance", "Maintenance tasks", "What maintenance tasks are described in this document?"),
    ("safety", "Safety warnings", "What safety warnings are described in this document?"),
    ("procedure", "Procedures", "What procedures are described in this document?"),
    ("troubleshooting", "Troubleshooting", "What troubleshooting information is described in this document?"),
)


class DeterministicPlanner:
    def __init__(self, *, id_generator: IdGenerator | None = None) -> None:
        self.id_generator = id_generator or IdGenerator()

    def create_plan(self, state: AgentState) -> ExecutionPlan | None:
        normalized_input = self._normalize(
            state.get("question") or state.get("user_input") or ""
        )
        if not self._looks_compound(normalized_input):
            return None

        explicit_document_id = state.get("document_id")
        selected_document_id = state.get("selected_document_id")
        document_query = state.get("document_query")
        document_id = explicit_document_id or selected_document_id
        document_title = state.get("document_title") or state.get("selected_document_title")

        if self._is_list_and_find_request(normalized_input):
            return self._build_list_and_find_plan(
                normalized_input=normalized_input,
                document_query=document_query,
                document_id=document_id,
                document_title=document_title,
            )

        if self._is_compare_request(normalized_input):
            return self._build_compare_plan(
                normalized_input=normalized_input,
                document_query=document_query,
                document_id=document_id,
                document_title=document_title,
            )

        if self._is_explore_and_answer_request(normalized_input):
            return self._build_explore_and_answer_plan(
                normalized_input=normalized_input,
                document_query=document_query,
                document_id=document_id,
                document_title=document_title,
            )

        if self._is_retrieve_and_answer_request(normalized_input):
            return self._build_retrieve_and_answer_plan(
                normalized_input=normalized_input,
                document_query=document_query,
                document_id=document_id,
                document_title=document_title,
            )
        return None

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.strip().lower().split())

    def _looks_compound(self, normalized_input: str) -> bool:
        if any(marker in f" {normalized_input} " for marker in _COMPOUND_MARKERS):
            return True
        keyword_hits = sum(
            1 for keyword in _TASK_KEYWORDS if keyword in normalized_input
        )
        return keyword_hits >= 2 and " and " in f" {normalized_input} "

    @staticmethod
    def _is_explore_and_answer_request(normalized_input: str) -> bool:
        return "explore" in normalized_input and any(
            marker in normalized_input
            for marker in ("list ", "summarize", "maintenance", "specification", "safety")
        )

    @staticmethod
    def _is_retrieve_and_answer_request(normalized_input: str) -> bool:
        return any(
            marker in normalized_input
            for marker in ("retrieve evidence", "show context", "summarize evidence")
        ) and any(marker in normalized_input for marker in ("summarize", "answer", "it"))

    @staticmethod
    def _is_compare_request(normalized_input: str) -> bool:
        return "compare" in normalized_input and " and " in normalized_input

    @staticmethod
    def _is_list_and_find_request(normalized_input: str) -> bool:
        return "show documents" in normalized_input and any(
            marker in normalized_input for marker in ("open ", "find ", "open document")
        )

    def _build_explore_and_answer_plan(
        self,
        *,
        normalized_input: str,
        document_query: str | None,
        document_id: str | None,
        document_title: str | None,
    ) -> ExecutionPlan:
        plan_steps = self._document_resolution_steps(document_query=document_query, document_id=document_id)
        plan_steps.append(
            self._step(
                tool_name="explore_document",
                description="Explore the selected document.",
                output_key="exploration",
            )
        )
        plan_steps.append(
            self._step(
                tool_name="answer_question",
                description="Answer the requested follow-up question against the same document.",
                output_key="answer",
                args={"question": self._build_follow_up_question(normalized_input)},
            )
        )
        return self._plan(
            goal=normalized_input,
            steps=plan_steps,
            reason="Detected a compound request that needs document exploration plus grounded answering.",
            requires_document=True,
            document_id=document_id,
            document_title=document_title or document_query,
            diagnostics={"plan_kind": "explore_answer"},
        )

    def _build_retrieve_and_answer_plan(
        self,
        *,
        normalized_input: str,
        document_query: str | None,
        document_id: str | None,
        document_title: str | None,
    ) -> ExecutionPlan:
        plan_steps = self._document_resolution_steps(document_query=document_query, document_id=document_id)
        retrieval_question = self._extract_retrieval_subject(normalized_input)
        plan_steps.append(
            self._step(
                tool_name="retrieve_chunks",
                description="Retrieve evidence chunks for the requested topic.",
                output_key="retrieved_evidence",
                args={"query_text": retrieval_question},
            )
        )
        plan_steps.append(
            self._step(
                tool_name="answer_question",
                description="Summarize the retrieved evidence as an answer.",
                input_key="retrieved_evidence",
                output_key="answer",
                args={"question": self._build_summary_question(retrieval_question)},
                depends_on=["retrieved_evidence"],
            )
        )
        return self._plan(
            goal=normalized_input,
            steps=plan_steps,
            reason="Detected a compound request that needs retrieval followed by deterministic answer generation.",
            requires_document=True,
            document_id=document_id,
            document_title=document_title or document_query,
            diagnostics={"plan_kind": "retrieve_answer"},
        )

    def _build_compare_plan(
        self,
        *,
        normalized_input: str,
        document_query: str | None,
        document_id: str | None,
        document_title: str | None,
    ) -> ExecutionPlan:
        comparison_topics = self._comparison_topics(normalized_input)
        plan_steps = self._document_resolution_steps(document_query=document_query, document_id=document_id)
        for index, (_, label, question) in enumerate(comparison_topics[:2], start=1):
            output_key = f"answer_{index}"
            plan_steps.append(
                self._step(
                    tool_name="answer_question",
                    description=f"Answer the {label.lower()} part of the comparison.",
                    output_key=output_key,
                    args={"question": question, "section_label": label},
                )
            )
        plan_steps.append(
            self._step(
                tool_name="format_combined_answer",
                description="Combine both grounded answers into a deterministic comparison response.",
                output_key="combined_answer",
                depends_on=["answer_1", "answer_2"],
                args={
                    "section_labels": [topic[1] for topic in comparison_topics[:2]],
                    "comparison_title": "Comparison",
                },
            )
        )
        return self._plan(
            goal=normalized_input,
            steps=plan_steps,
            reason="Detected a comparison request that needs multiple grounded answer steps.",
            requires_document=True,
            document_id=document_id,
            document_title=document_title or document_query,
            diagnostics={
                "plan_kind": "compare_answers",
                "comparison_labels": [topic[1] for topic in comparison_topics[:2]],
            },
        )

    def _build_list_and_find_plan(
        self,
        *,
        normalized_input: str,
        document_query: str | None,
        document_id: str | None,
        document_title: str | None,
    ) -> ExecutionPlan:
        target_query = document_query or self._extract_open_target(normalized_input)
        steps = [
            self._step(
                tool_name="list_documents",
                description="List available documents.",
                output_key="listed_documents",
            ),
            self._step(
                tool_name="find_document",
                description="Find the requested document from the available list.",
                output_key="resolved_document",
                args={"query_text": target_query},
                depends_on=["listed_documents"],
            ),
        ]
        return self._plan(
            goal=normalized_input,
            steps=steps,
            reason="Detected a compound request that first lists the corpus and then resolves a target document.",
            requires_document=False,
            document_id=document_id,
            document_title=document_title or target_query,
            diagnostics={"plan_kind": "list_and_find"},
        )

    def _document_resolution_steps(
        self,
        *,
        document_query: str | None,
        document_id: str | None,
    ) -> list[PlanStep]:
        if document_id or not document_query:
            return []
        return [
            self._step(
                tool_name="find_document",
                description="Resolve the requested document before executing the remaining steps.",
                output_key="resolved_document",
                args={"query_text": document_query},
            )
        ]

    def _plan(
        self,
        *,
        goal: str,
        steps: Sequence[PlanStep],
        reason: str,
        requires_document: bool,
        document_id: str | None,
        document_title: str | None,
        diagnostics: dict[str, object],
    ) -> ExecutionPlan:
        resolved_diagnostics = {
            "planner_confidence": 0.95,
            **diagnostics,
        }
        return ExecutionPlan(
            plan_id=self.id_generator.new_id("plan"),
            goal=goal,
            steps=list(steps),
            reason=reason,
            requires_document=requires_document,
            document_id=document_id,
            document_title=document_title,
            diagnostics=resolved_diagnostics,
        )

    def _step(
        self,
        *,
        tool_name: str,
        description: str,
        output_key: str,
        input_key: str | None = None,
        args: dict[str, object] | None = None,
        depends_on: list[str] | None = None,
        required: bool = True,
    ) -> PlanStep:
        return PlanStep(
            step_id=self.id_generator.new_id("step"),
            tool_name=tool_name,
            description=description,
            input_key=input_key,
            output_key=output_key,
            args=dict(args or {}),
            depends_on=list(depends_on or []),
            required=required,
        )

    def _comparison_topics(
        self,
        normalized_input: str,
    ) -> list[tuple[str, str, str]]:
        topics: list[tuple[int, tuple[str, str, str]]] = []
        for topic in _COMPARISON_TOPICS:
            marker = topic[0]
            index = normalized_input.find(marker)
            if index >= 0:
                topics.append((index, topic))
        topics.sort(key=lambda item: item[0])
        resolved = [topic for _, topic in topics]
        if len(resolved) >= 2:
            return resolved
        return [
            _COMPARISON_TOPICS[0],
            _COMPARISON_TOPICS[1],
        ]

    @staticmethod
    def _extract_retrieval_subject(normalized_input: str) -> str:
        for marker in ("retrieve evidence for ", "show context for ", "summarize evidence for "):
            if marker in normalized_input:
                tail = normalized_input.split(marker, 1)[1]
                tail = tail.split(" and ", 1)[0].strip()
                if tail:
                    return tail
        return normalized_input

    @staticmethod
    def _build_summary_question(subject: str) -> str:
        return f"Summarize the evidence for {subject}."

    @staticmethod
    def _build_follow_up_question(normalized_input: str) -> str:
        if "maintenance" in normalized_input:
            return "What maintenance tasks are described in this document?"
        if "specification" in normalized_input:
            return "What specifications are available in this document?"
        if "safety" in normalized_input:
            return "What safety warnings are described in this document?"
        return normalized_input

    @staticmethod
    def _extract_open_target(normalized_input: str) -> str | None:
        for marker in ("open ", "open document ", "find document "):
            if marker in normalized_input:
                tail = normalized_input.split(marker, 1)[1].strip()
                if tail:
                    return tail
        return None
