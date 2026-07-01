from __future__ import annotations

import re

from src.application.langgraph.research.models import (
    ResearchGoalType,
    ResearchOutputType,
    ResearchPlan,
)
from src.application.langgraph.research.planners.research_plan_builder import (
    ResearchPlanBuilder,
)
from src.application.langgraph.research.policies import ResearchPolicy
from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)
from src.application.langgraph.strategy_advisor.advisor_models import (
    StrategyAdvisorIntent,
    StrategyAdvisorProposal,
)

_COMPARE_PREFIX_RE = re.compile(
    r"^(?:compare|contrast|difference between|differences between|relationship between|how does)\s+",
    re.IGNORECASE,
)
_SPLIT_RE = re.compile(r"\s+(?:and|versus|vs|with)\s+", re.IGNORECASE)
_FILLER_RE = re.compile(
    r"\b(?:generate|create|build|prepare|produce|give|show|summarize|analyse|analyze|research|report|checklist|document|manual|datasheet|certificate|drawing|all|across|the)\b",
    re.IGNORECASE,
)
_WHITESPACE_RE = re.compile(r"\s+")
_CATEGORY_PATTERNS: tuple[tuple[re.Pattern[str], RetrievalStrategy], ...] = (
    (
        re.compile(
            r"\b(?:part\s*number|part\s*no\.?|p/?n\.?|serial\s*number|serial\s*no\.?|s/?n\.?|model\s*number|model\s*no\.?|drawing\s*number|drawing\s*no\.?|component\s*code|identifier|[A-Z]{2,3}-\d{3,})\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.IDENTIFIER_LOOKUP,
    ),
    (
        re.compile(
            r"\b(?:troubleshoot|troubleshooting|fault|error|alarm|failure|symptom|cause|remedy|recovery)\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.TROUBLESHOOTING_LOOKUP,
    ),
    (
        re.compile(
            r"\b(?:maintenance|preventive maintenance|service|servicing|inspection|interval|schedule|lubrication|lubricate)\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.MAINTENANCE_LOOKUP,
    ),
    (
        re.compile(
            r"\b(?:procedure|procedures|startup|start up|shutdown|shut down|commissioning|commission|operation|operate|install|installation|remove|replacement|replace)\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.PROCEDURE_LOOKUP,
    ),
    (
        re.compile(
            r"\b(?:specification|specifications|technical data|technical|pressure|temperature|voltage|power|capacity|rating|dimension|dimensions|material|operating limit|limits)\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.TECHNICAL_SPECIFICATION,
    ),
    (
        re.compile(
            r"\b(?:certificate|certification|approval|compliance|atex|iecex|surveyor)\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.CERTIFICATION_LOOKUP,
    ),
    (
        re.compile(
            r"\b(?:drawing|diagram|schematic|layout|title block)\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.DRAWING_LOOKUP,
    ),
    (
        re.compile(r"\b(?:figure|image|picture)\b", re.IGNORECASE),
        RetrievalStrategy.FIGURE_LOOKUP,
    ),
    (
        re.compile(
            r"\b(?:table|tables|matrix|list|lists|rows|columns|ordering example)\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.TABLE_LOOKUP,
    ),
)
_TABLE_HINT_RE = re.compile(
    r"\b(?:table|tables|schedule|matrix|rows|columns|specification table|ordering example|comparison table)\b",
    re.IGNORECASE,
)


class DeterministicResearchPlanner:
    def __init__(self, *, plan_builder: ResearchPlanBuilder | None = None) -> None:
        self.plan_builder = plan_builder or ResearchPlanBuilder()

    def plan(
        self,
        *,
        user_input: str,
        document_id: str | None,
        document_title: str | None,
        policy: ResearchPolicy,
        advisor_proposal: StrategyAdvisorProposal | None = None,
    ) -> ResearchPlan:
        goal = self.plan_builder.build_goal(
            user_input=user_input,
            document_id=document_id,
            document_title=document_title,
        )
        self._apply_goal_overrides(goal, advisor_proposal=advisor_proposal)
        concepts = self._resolve_concepts(
            user_input=user_input,
            goal_type=goal.goal_type,
            advisor_proposal=advisor_proposal,
        )
        goal.requires_cross_section_reasoning = goal.goal_type in {
            ResearchGoalType.COMPARISON,
            ResearchGoalType.CHECKLIST,
            ResearchGoalType.AUDIT,
            ResearchGoalType.GAP_ANALYSIS,
            ResearchGoalType.REPORT,
        }
        goal.requires_multi_strategy_retrieval = len(concepts) > 1 or goal.goal_type in {
            ResearchGoalType.COMPARISON,
            ResearchGoalType.REPORT,
            ResearchGoalType.GAP_ANALYSIS,
            ResearchGoalType.AUDIT,
        }
        goal.expected_output_type = self._output_type(goal.goal_type)
        goal.diagnostics.update(
            {
                "concepts": list(concepts),
                "advisor_intent": (
                    advisor_proposal.intent.value
                    if advisor_proposal is not None
                    else None
                ),
                "advisor_requires_table": (
                    advisor_proposal.requires_table
                    if advisor_proposal is not None
                    else False
                ),
            }
        )
        tasks = self._tasks_for_goal(
            goal=goal,
            concepts=concepts,
            policy=policy,
            advisor_proposal=advisor_proposal,
        )
        return self.plan_builder.build_plan(
            goal=goal,
            tasks=tasks,
            reason=self._reason(goal.goal_type, concepts),
            source="deterministic",
            policy=policy,
        )

    def _apply_goal_overrides(
        self,
        goal,
        *,
        advisor_proposal: StrategyAdvisorProposal | None,
    ) -> None:
        if advisor_proposal is None:
            return
        mapping = {
            StrategyAdvisorIntent.COMPARISON: ResearchGoalType.COMPARISON,
            StrategyAdvisorIntent.SUMMARY: ResearchGoalType.SUMMARY,
            StrategyAdvisorIntent.CHECKLIST: ResearchGoalType.CHECKLIST,
            StrategyAdvisorIntent.REPORT: ResearchGoalType.REPORT,
            StrategyAdvisorIntent.EVIDENCE_REVIEW: ResearchGoalType.EVIDENCE_REVIEW,
            StrategyAdvisorIntent.GENERAL_LOOKUP: goal.goal_type,
        }
        if advisor_proposal.comparison:
            goal.goal_type = ResearchGoalType.COMPARISON
            return
        goal.goal_type = mapping.get(advisor_proposal.intent, goal.goal_type)

    def _tasks_for_goal(
        self,
        *,
        goal,
        concepts: list[str],
        policy: ResearchPolicy,
        advisor_proposal: StrategyAdvisorProposal | None,
    ) -> list:
        if goal.goal_type == ResearchGoalType.COMPARISON:
            return self._comparison_tasks(
                goal=goal,
                concepts=concepts,
                policy=policy,
                advisor_proposal=advisor_proposal,
            )
        if goal.goal_type == ResearchGoalType.CHECKLIST:
            return self._checklist_tasks(
                goal=goal,
                concepts=concepts,
                policy=policy,
            )
        if goal.goal_type in {
            ResearchGoalType.GAP_ANALYSIS,
            ResearchGoalType.EVIDENCE_REVIEW,
        }:
            return self._evidence_review_tasks(goal=goal, concepts=concepts, policy=policy)
        return self._general_tasks(
            goal=goal,
            concepts=concepts,
            policy=policy,
            advisor_proposal=advisor_proposal,
        )

    def _comparison_tasks(
        self,
        *,
        goal,
        concepts: list[str],
        policy: ResearchPolicy,
        advisor_proposal: StrategyAdvisorProposal | None,
    ) -> list:
        tasks = [
            self._task_for_concept(
                goal=goal,
                concept=concept,
                question=f"What evidence in this document describes {concept}?",
                strategy=self._strategy_for_concept(concept),
                answer_intent="comparison",
                max_results=policy.max_evidence_per_task,
            )
            for concept in concepts
        ]
        concept_text = self._concept_list_text(concepts)
        tasks.append(
            self.plan_builder.build_task(
                title="Collect overlap evidence",
                question=f"What shared requirements, overlaps, or relationships connect {concept_text} in this document?",
                strategy_hint=RetrievalStrategy.GENERAL_HYBRID.value,
                answer_intent_hint="comparison",
                document_id=goal.document_id,
                required=False,
                expected_evidence_type="overlap",
                max_results=policy.max_evidence_per_task,
                diagnostics={"concept_role": "overlap"},
            )
        )
        tasks.append(
            self.plan_builder.build_task(
                title="Collect distinguishing evidence",
                question=f"What differences distinguish {concept_text} in this document?",
                strategy_hint=RetrievalStrategy.GENERAL_HYBRID.value,
                answer_intent_hint="comparison",
                document_id=goal.document_id,
                required=False,
                expected_evidence_type="difference",
                max_results=policy.max_evidence_per_task,
                diagnostics={"concept_role": "difference"},
            )
        )
        if self._requires_table(concepts, advisor_proposal):
            tasks.append(
                self.plan_builder.build_task(
                    title="Collect structured comparison evidence",
                    question=f"What tables, schedules, or structured rows compare {concept_text}?",
                    strategy_hint=RetrievalStrategy.TABLE_LOOKUP.value,
                    answer_intent_hint="comparison",
                    document_id=goal.document_id,
                    required=False,
                    expected_evidence_type="comparison_table",
                    max_results=max(4, policy.max_evidence_per_task // 2),
                    diagnostics={"concept_role": "table_support"},
                )
            )
        return tasks

    def _checklist_tasks(
        self,
        *,
        goal,
        concepts: list[str],
        policy: ResearchPolicy,
    ) -> list:
        tasks = [
            self._task_for_concept(
                goal=goal,
                concept=concept,
                question=f"What steps, checks, or requirements are described for {concept}?",
                strategy=self._strategy_for_concept(concept),
                answer_intent="checklist",
                max_results=policy.max_evidence_per_task,
            )
            for concept in concepts
        ]
        concept_text = self._concept_list_text(concepts)
        tasks.append(
            self.plan_builder.build_task(
                title="Collect safety warnings",
                question=f"What safety warnings or prerequisites apply to {concept_text}?",
                strategy_hint=RetrievalStrategy.SECTION_LOOKUP.value,
                answer_intent_hint="checklist",
                document_id=goal.document_id,
                required=False,
                expected_evidence_type="safety",
                max_results=policy.max_evidence_per_task,
                diagnostics={"concept_role": "safety"},
            )
        )
        tasks.append(
            self.plan_builder.build_task(
                title="Collect prerequisites",
                question=f"What prerequisite checks or preparation steps are required for {concept_text}?",
                strategy_hint=RetrievalStrategy.PROCEDURE_LOOKUP.value,
                answer_intent_hint="checklist",
                document_id=goal.document_id,
                required=False,
                expected_evidence_type="prerequisite",
                max_results=policy.max_evidence_per_task,
                diagnostics={"concept_role": "prerequisite"},
            )
        )
        return tasks

    def _evidence_review_tasks(
        self,
        *,
        goal,
        concepts: list[str],
        policy: ResearchPolicy,
    ) -> list:
        concept_text = self._concept_list_text(concepts)
        tasks = [
            self.plan_builder.build_task(
                title="Collect primary evidence",
                question=goal.user_input,
                strategy_hint=RetrievalStrategy.GENERAL_HYBRID.value,
                answer_intent_hint="evidence_review",
                document_id=goal.document_id,
                expected_evidence_type="claim_evidence",
                max_results=policy.max_evidence_per_task,
                diagnostics={"concepts": list(concepts)},
            ),
            self.plan_builder.build_task(
                title="Collect related sections",
                question=f"What related sections provide context for {concept_text}?",
                strategy_hint=RetrievalStrategy.SECTION_LOOKUP.value,
                answer_intent_hint="evidence_review",
                document_id=goal.document_id,
                required=False,
                expected_evidence_type="gap_probe",
                max_results=max(3, policy.max_evidence_per_task // 2),
                diagnostics={"concepts": list(concepts), "concept_role": "context"},
            ),
        ]
        return tasks

    def _general_tasks(
        self,
        *,
        goal,
        concepts: list[str],
        policy: ResearchPolicy,
        advisor_proposal: StrategyAdvisorProposal | None,
    ) -> list:
        tasks = [
            self._task_for_concept(
                goal=goal,
                concept=concept,
                question=f"What evidence in this document describes {concept}?",
                strategy=self._strategy_for_concept(concept),
                answer_intent=self._general_answer_intent(goal.goal_type),
                max_results=policy.max_evidence_per_task,
            )
            for concept in concepts
        ]
        concept_text = self._concept_list_text(concepts)
        tasks.append(
            self.plan_builder.build_task(
                title="Collect overview evidence",
                question=f"What overview or summary sections explain {concept_text} in this document?",
                strategy_hint=RetrievalStrategy.SECTION_LOOKUP.value,
                answer_intent_hint=self._general_answer_intent(goal.goal_type),
                document_id=goal.document_id,
                required=False,
                expected_evidence_type="overview",
                max_results=max(3, policy.max_evidence_per_task // 2),
                diagnostics={"concept_role": "overview"},
            )
        )
        if self._requires_table(concepts, advisor_proposal):
            tasks.append(
                self.plan_builder.build_task(
                    title="Collect structured evidence",
                    question=f"What structured tables, schedules, or lists support {concept_text}?",
                    strategy_hint=RetrievalStrategy.TABLE_LOOKUP.value,
                    answer_intent_hint=self._general_answer_intent(goal.goal_type),
                    document_id=goal.document_id,
                    required=False,
                    expected_evidence_type="structured_support",
                    max_results=max(4, policy.max_evidence_per_task // 2),
                    diagnostics={"concept_role": "table_support"},
                )
            )
        return tasks

    def _task_for_concept(
        self,
        *,
        goal,
        concept: str,
        question: str,
        strategy: RetrievalStrategy,
        answer_intent: str,
        max_results: int,
    ):
        return self.plan_builder.build_task(
            title=f"Collect evidence for {concept}",
            question=question,
            strategy_hint=strategy.value,
            answer_intent_hint=answer_intent,
            document_id=goal.document_id,
            expected_evidence_type=self._normalize_theme(concept),
            max_results=max_results,
            diagnostics={
                "concept": concept,
                "concept_role": "primary",
                "strategy_hint": strategy.value,
            },
        )

    def _resolve_concepts(
        self,
        *,
        user_input: str,
        goal_type: ResearchGoalType,
        advisor_proposal: StrategyAdvisorProposal | None,
    ) -> list[str]:
        if advisor_proposal is not None and advisor_proposal.concepts:
            return self._deduplicate_concepts(advisor_proposal.concepts)
        if goal_type == ResearchGoalType.COMPARISON:
            concepts = self._split_compare_concepts(user_input)
            if concepts:
                return concepts
        keyword_concepts = self._keyword_concepts(user_input)
        if keyword_concepts:
            return keyword_concepts
        fallback = self._fallback_focus_phrase(user_input)
        return [fallback] if fallback else ["document evidence"]

    @staticmethod
    def _split_compare_concepts(user_input: str) -> list[str]:
        value = _COMPARE_PREFIX_RE.sub("", user_input.strip())
        parts = [
            DeterministicResearchPlanner._clean_phrase(part)
            for part in _SPLIT_RE.split(value)
        ]
        concepts = [part for part in parts if part]
        return DeterministicResearchPlanner._deduplicate_concepts(concepts)

    @staticmethod
    def _keyword_concepts(user_input: str) -> list[str]:
        matches: list[str] = []
        value = user_input.strip()
        for pattern, _strategy in _CATEGORY_PATTERNS:
            match = pattern.search(value)
            if match is None:
                continue
            phrase = DeterministicResearchPlanner._clean_phrase(match.group(0))
            if phrase:
                matches.append(phrase)
        return DeterministicResearchPlanner._deduplicate_concepts(matches)

    @staticmethod
    def _fallback_focus_phrase(user_input: str) -> str:
        value = _COMPARE_PREFIX_RE.sub("", user_input.strip())
        value = _FILLER_RE.sub(" ", value)
        return DeterministicResearchPlanner._clean_phrase(value)

    @staticmethod
    def _clean_phrase(value: str) -> str:
        cleaned = _FILLER_RE.sub(" ", value)
        cleaned = _WHITESPACE_RE.sub(" ", cleaned).strip(" ,.;:-")
        return cleaned

    @staticmethod
    def _deduplicate_concepts(concepts: list[str]) -> list[str]:
        ordered: list[str] = []
        seen: set[str] = set()
        for concept in concepts:
            normalized = DeterministicResearchPlanner._normalize_theme(concept)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            ordered.append(concept)
        return ordered

    @staticmethod
    def _normalize_theme(value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", " ", value.strip().lower())
        return " ".join(normalized.split())

    @staticmethod
    def _strategy_for_concept(concept: str) -> RetrievalStrategy:
        for pattern, strategy in _CATEGORY_PATTERNS:
            if pattern.search(concept):
                return strategy
        return RetrievalStrategy.GENERAL_HYBRID

    @staticmethod
    def _requires_table(
        concepts: list[str],
        advisor_proposal: StrategyAdvisorProposal | None,
    ) -> bool:
        if advisor_proposal is not None and advisor_proposal.requires_table:
            return True
        return any(_TABLE_HINT_RE.search(concept) for concept in concepts)

    @staticmethod
    def _general_answer_intent(goal_type: ResearchGoalType) -> str:
        return {
            ResearchGoalType.REPORT: "research_report",
            ResearchGoalType.SUMMARY: "research_summary",
            ResearchGoalType.GENERAL_RESEARCH: "research",
            ResearchGoalType.AUDIT: "research_audit",
        }.get(goal_type, "research")

    @staticmethod
    def _concept_list_text(concepts: list[str]) -> str:
        if not concepts:
            return "the request topics"
        if len(concepts) == 1:
            return concepts[0]
        return ", ".join(concepts[:-1]) + f", and {concepts[-1]}"

    @staticmethod
    def _output_type(goal_type: ResearchGoalType) -> ResearchOutputType:
        mapping = {
            ResearchGoalType.COMPARISON: ResearchOutputType.COMPARISON,
            ResearchGoalType.SUMMARY: ResearchOutputType.SUMMARY,
            ResearchGoalType.CHECKLIST: ResearchOutputType.CHECKLIST,
            ResearchGoalType.AUDIT: ResearchOutputType.AUDIT,
            ResearchGoalType.EVIDENCE_REVIEW: ResearchOutputType.EVIDENCE_REVIEW,
            ResearchGoalType.GAP_ANALYSIS: ResearchOutputType.EVIDENCE_REVIEW,
            ResearchGoalType.REPORT: ResearchOutputType.REPORT,
            ResearchGoalType.GENERAL_RESEARCH: ResearchOutputType.REPORT,
        }
        return mapping[goal_type]

    @staticmethod
    def _reason(goal_type: ResearchGoalType, concepts: list[str]) -> str:
        concept_text = DeterministicResearchPlanner._concept_list_text(concepts)
        return {
            ResearchGoalType.COMPARISON: (
                f"The request compares {concept_text}, so the plan collects evidence "
                "for each concept plus overlap and difference support."
            ),
            ResearchGoalType.SUMMARY: (
                f"The request asks for a document-wide summary of {concept_text}."
            ),
            ResearchGoalType.CHECKLIST: (
                f"The request needs a checklist assembled from {concept_text}, safety, "
                "and prerequisite evidence."
            ),
            ResearchGoalType.AUDIT: (
                f"The request needs cross-section audit evidence for {concept_text}."
            ),
            ResearchGoalType.EVIDENCE_REVIEW: (
                f"The request needs supporting evidence and related context for {concept_text}."
            ),
            ResearchGoalType.GAP_ANALYSIS: (
                f"The request needs supporting evidence and missing-evidence detection for {concept_text}."
            ),
            ResearchGoalType.REPORT: (
                f"The request needs a structured research report about {concept_text}."
            ),
            ResearchGoalType.GENERAL_RESEARCH: (
                f"The request needs broader document research about {concept_text}."
            ),
        }[goal_type]
